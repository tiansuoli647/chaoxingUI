# -*- coding: utf-8 -*-
import os
import shutil
import sys
import threading
import time
import re
import builtins
import configparser
import traceback
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from loguru import logger

# Create Flask app
app = Flask(__name__, static_folder="static")

# Configuration paths
CONFIG_PATH = "config.ini"
TEMPLATE_PATH = "config_template.ini"

# Global state
ACTIVE_CHAOXING = None
BRUSH_THREAD = None
STOP_EVENT = threading.Event()

TASK_STATE = {
    "status": "idle",  # "idle", "running", "error", "completed"
    "current_course": "-",
    "current_chapter": "-",
    "logs": [],
    "error_message": ""
}

STATE_LOCK = threading.Lock()

class WebLogSink:
    def __init__(self):
        pass
        
    def write(self, message):
        clean_msg = str(message).strip()
        if not clean_msg:
            return
            
        with STATE_LOCK:
            TASK_STATE["logs"].append(clean_msg)
            # Limit logs in memory
            if len(TASK_STATE["logs"]) > 1500:
                TASK_STATE["logs"].pop(0)
                
            # Parse progress states from logs
            if "开始学习课程:" in clean_msg:
                match = re.search(r"开始学习课程:\s*(.*)", clean_msg)
                if match:
                    TASK_STATE["current_course"] = match.group(1)
            elif "当前章节:" in clean_msg:
                match = re.search(r"当前章节:\s*(.*)", clean_msg)
                if match:
                    TASK_STATE["current_chapter"] = match.group(1)
            elif "所有课程学习任务已完成" in clean_msg:
                TASK_STATE["status"] = "completed"
                TASK_STATE["current_course"] = "已完成"
                TASK_STATE["current_chapter"] = "已完成"
            elif "========== 任务已成功停止 ==========" in clean_msg or "========== 任务被用户强行终止 ==========" in clean_msg:
                TASK_STATE["status"] = "idle"
                TASK_STATE["current_course"] = "-"
                TASK_STATE["current_chapter"] = "-"
                TASK_STATE["error_message"] = ""
            elif ("错误:" in clean_msg or "Error in thread" in clean_msg) and "用户已通过网页终止" not in clean_msg and "网页终止" not in clean_msg:
                TASK_STATE["status"] = "error"
                TASK_STATE["error_message"] = clean_msg

web_log_sink = WebLogSink()

def initialize_config():
    """Ensure config.ini exists, copying from template if necessary."""
    if not os.path.exists(CONFIG_PATH):
        if os.path.exists(TEMPLATE_PATH):
            shutil.copy(TEMPLATE_PATH, CONFIG_PATH)
        else:
            # Create a basic skeleton if template is missing
            with open(CONFIG_PATH, "w", encoding="utf8") as f:
                f.write("[common]\nuse_cookies=false\nusername=\npassword=\nspeed=1\njobs=4\n")

initialize_config()

def read_config():
    """Read the config file and return sections as a dictionary."""
    initialize_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf8")
    
    data = {}
    for section in config.sections():
        data[section] = {}
        for key, val in config.items(section):
            data[section][key] = val
    return data

def write_config(data):
    """Write configuration dictionary to config.ini."""
    config = configparser.ConfigParser()
    # Read first to keep comments or structure if possible (optional)
    config.read(CONFIG_PATH, encoding="utf8")
    
    for section, keys in data.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, val in keys.items():
            config.set(section, key, str(val))
            
    with open(CONFIG_PATH, "w", encoding="utf8") as f:
        config.write(f)

def readd_log_sink():
    try:
        from loguru import logger
        logger.add(web_log_sink.write, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}", level="INFO")
    except Exception:
        pass

# Initial log sink registration
readd_log_sink()

@app.route("/")
def index():
    """Serve the single-page application."""
    # Since templates folder might not exist yet, we will serve index.html directly from templates/index.html
    # if it exists, otherwise return a placeholder.
    templates_dir = os.path.join(app.root_path, "templates")
    if os.path.exists(os.path.join(templates_dir, "index.html")):
        return send_from_directory(templates_dir, "index.html")
    return "templates/index.html not created yet."

@app.route("/api/config", methods=["GET"])
def get_config():
    try:
        return jsonify({"status": "success", "config": read_config()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/config", methods=["POST"])
def post_config():
    try:
        req_data = request.json
        if not req_data or "config" not in req_data:
            return jsonify({"status": "error", "message": "Missing config data"}), 400
        write_config(req_data["config"])
        return jsonify({"status": "success", "message": "Config saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def do_login():
    global ACTIVE_CHAOXING
    try:
        req_data = request.json or {}
        username = req_data.get("username", "").strip()
        password = req_data.get("password", "").strip()
        use_cookies = req_data.get("use_cookies", False)
        
        # Save credentials to config
        current_config = read_config()
        if "common" not in current_config:
            current_config["common"] = {}
        current_config["common"]["username"] = username
        current_config["common"]["password"] = password
        current_config["common"]["use_cookies"] = "true" if use_cookies else "false"
        write_config(current_config)
        
        # Initialize Chaoxing core APIs
        # We need to import classes locally to ensure they load after pip finishes installation
        from api.base import Account, Chaoxing
        from api.answer import Tiku
        
        # Re-register our log sink because importing api.base imports api.logger which removes all sinks
        readd_log_sink()
        
        account = Account(username, password)
        tiku = Tiku()
        
        # Read tiku config to initialize
        tiku_config = current_config.get("tiku", {})
        tiku.config_set(tiku_config)
        tiku = tiku.get_tiku_from_config()
        tiku.init_tiku()
        
        query_delay = float(tiku_config.get("delay", 1.0))
        
        chaoxing = Chaoxing(account=account, tiku=tiku, query_delay=query_delay)
        
        # Attempt Login
        login_res = chaoxing.login(login_with_cookies=use_cookies)
        if not login_res.get("status"):
            return jsonify({"status": "error", "message": login_res.get("msg", "登录失败")})
            
        ACTIVE_CHAOXING = chaoxing
        return jsonify({
            "status": "success", 
            "message": "登录成功", 
            "user_info": {
                "name": login_res.get("name", "学习通用户"),
                "uid": chaoxing.get_uid()
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"登录发生异常: {str(e)}"}), 500

@app.route("/api/courses", methods=["GET"])
def get_courses():
    global ACTIVE_CHAOXING
    if not ACTIVE_CHAOXING:
        return jsonify({"status": "error", "message": "请先完成登录"}), 401
    try:
        courses = ACTIVE_CHAOXING.get_course_list()
        return jsonify({"status": "success", "courses": courses})
    except Exception as e:
        return jsonify({"status": "error", "message": f"获取课程失败: {str(e)}"}), 500

# Monkeypatching functions to handle stop command and avoid CLI inputs
def make_monkeypatches(stop_event):
    import requests
    import queue
    original_request = requests.Session.request
    original_sleep = time.sleep
    original_get = queue.Queue.get
    
    def custom_request(self, method, url, *args, **kwargs):
        if stop_event.is_set():
            raise KeyboardInterrupt("用户已通过网页终止任务")
        return original_request(self, method, url, *args, **kwargs)
        
    def custom_sleep(seconds):
        start = time.time()
        step = 0.1
        while time.time() - start < seconds:
            if stop_event.is_set():
                raise KeyboardInterrupt("用户已通过网页终止任务")
            original_sleep(min(step, seconds - (time.time() - start)))
            
    def custom_get(self, block=True, timeout=None):
        if stop_event.is_set():
            raise KeyboardInterrupt("用户已通过网页终止任务")
        return original_get(self, block, timeout)
            
    # Mock builtins.input to prevent CLI from blocking
    def custom_input(prompt=""):
        # Automatically say yes to continue
        logger.info(f"[WebUI-AutoInput] 自动回答 input 提示 '{prompt.strip()}' 为 'y'")
        return "y"
        
    return custom_request, custom_sleep, custom_input, custom_get, original_request, original_sleep, original_get

def run_brush_task(course_ids):
    global ACTIVE_CHAOXING
    
    # Setup stop event and monkeypatches
    STOP_EVENT.clear()
    
    import requests
    import main
    
    # Re-register our log sink because importing main imports api.logger which removes all sinks
    readd_log_sink()
    
    # Track active JobProcessors to prevent join() deadlocks on manual stop
    global ACTIVE_JOB_PROCESSORS
    ACTIVE_JOB_PROCESSORS = []
    
    original_processor_init = main.JobProcessor.__init__
    def custom_processor_init(self, chaoxing, course, tasks, config):
        original_processor_init(self, chaoxing, course, tasks, config)
        ACTIVE_JOB_PROCESSORS.append(self)
        
    main.JobProcessor.__init__ = custom_processor_init
    
    # Get custom monkeypatch methods
    custom_request, custom_sleep, custom_input, custom_get, orig_req, orig_sleep, orig_get = make_monkeypatches(STOP_EVENT)
    orig_input = builtins.input
    
    # Apply patches
    import queue
    requests.Session.request = custom_request
    time.sleep = custom_sleep
    builtins.input = custom_input
    queue.Queue.get = custom_get
    
    try:
        with STATE_LOCK:
            TASK_STATE["status"] = "running"
            TASK_STATE["logs"] = []
            TASK_STATE["error_message"] = ""
            TASK_STATE["current_course"] = "-"
            TASK_STATE["current_chapter"] = "-"
            
        logger.info("========== 网页端刷课任务开始 ==========")
        logger.info(f"选定课程 ID 列表: {', '.join(course_ids)}")
        
        # Load configs
        common_config, tiku_config, notification_config = main.load_config_from_file(CONFIG_PATH)
        
        # Sync selected course list
        common_config["course_list"] = course_ids
        common_config["speed"] = min(2.0, max(1.0, common_config.get("speed", 1.0)))
        common_config["notopen_action"] = common_config.get("notopen_action", "retry")
        
        # Set up notification
        from api.notification import Notification
        notification = Notification()
        notification.config_set(notification_config)
        notification = notification.get_notification_from_config()
        notification.init_notification()
        
        # Filter selected courses
        all_courses = ACTIVE_CHAOXING.get_course_list()
        course_task = []
        for course in all_courses:
            if course["courseId"] in course_ids:
                course_task.append(course)
                
        if not course_task:
            logger.warning("未匹配到任何有效课程，请检查课程是否正确！")
            with STATE_LOCK:
                TASK_STATE["status"] = "idle"
            return
            
        logger.info(f"待学习课程过滤完毕，匹配课程数: {len(course_task)}")
        
        # Re-initialize Tiku from the latest config.ini in case they changed it after logging in!
        from api.answer import Tiku
        new_tiku = Tiku()
        new_tiku.config_set(tiku_config)
        new_tiku = new_tiku.get_tiku_from_config()
        new_tiku.init_tiku()
        
        # Assign the new tiku instance to ACTIVE_CHAOXING
        ACTIVE_CHAOXING.tiku = new_tiku
        logger.info(f"[WebUI-Debug] 动态重载题库: {new_tiku.name} ({new_tiku.__class__.__name__})")
        logger.info(f"[WebUI-Debug] ACTIVE_CHAOXING.tiku 现在是: {ACTIVE_CHAOXING.tiku.name} ({ACTIVE_CHAOXING.tiku.__class__.__name__})")
        ACTIVE_CHAOXING.query_delay = float(tiku_config.get("delay", 1.0))
        
        # Process each course
        for course in course_task:
            if STOP_EVENT.is_set():
                break
            main.process_course(ACTIVE_CHAOXING, course, common_config)
            
        if STOP_EVENT.is_set():
            logger.warning("========== 任务被用户强行终止 ==========")
            with STATE_LOCK:
                TASK_STATE["status"] = "idle"
        else:
            logger.info("========== 所有选定课程学习任务已完成！ ==========")
            notification.send("chaoxing Web : 所有选定课程学习任务已完成")
            with STATE_LOCK:
                TASK_STATE["status"] = "completed"
                
    except KeyboardInterrupt:
        logger.warning("========== 任务已成功停止 ==========")
        with STATE_LOCK:
            TASK_STATE["status"] = "idle"
    except Exception as e:
        err_msg = f"任务运行异常中断: {str(e)}\n{traceback.format_exc()}"
        logger.error(err_msg)
        with STATE_LOCK:
            TASK_STATE["status"] = "error"
            TASK_STATE["error_message"] = str(e)
    finally:
        # Revert monkeypatches
        import queue
        requests.Session.request = orig_req
        time.sleep = orig_sleep
        builtins.input = orig_input
        queue.Queue.get = orig_get
        
        # Revert JobProcessor init patch
        main.JobProcessor.__init__ = original_processor_init
        if 'ACTIVE_JOB_PROCESSORS' in globals():
            ACTIVE_JOB_PROCESSORS.clear()

@app.route("/api/start", methods=["POST"])
def start_brush():
    global BRUSH_THREAD, ACTIVE_CHAOXING
    if not ACTIVE_CHAOXING:
        return jsonify({"status": "error", "message": "请先登录"}), 400
        
    with STATE_LOCK:
        if TASK_STATE["status"] == "running":
            return jsonify({"status": "error", "message": "刷课任务已在运行中"}), 400
            
    req_data = request.json or {}
    course_ids = req_data.get("course_ids", [])
    if not course_ids:
        # If not specified, read from config.ini
        conf = read_config()
        course_str = conf.get("common", {}).get("course_list", "")
        course_ids = [c.strip() for c in course_str.split(",") if c.strip()]
        
    if not course_ids:
        return jsonify({"status": "error", "message": "未指定要学习的课程 ID"}), 400
        
    # Start thread
    BRUSH_THREAD = threading.Thread(target=run_brush_task, args=(course_ids,), daemon=True)
    BRUSH_THREAD.start()
    
    return jsonify({"status": "success", "message": "刷课后台任务已启动"})

@app.route("/api/stop", methods=["POST"])
def stop_brush():
    global STOP_EVENT, ACTIVE_JOB_PROCESSORS
    with STATE_LOCK:
        if TASK_STATE["status"] != "running":
            return jsonify({"status": "error", "message": "没有正在运行的任务"}), 400
            
    STOP_EVENT.set()
    
    # Release the join() blocks on all active task queues to prevent deadlocks
    try:
        if 'ACTIVE_JOB_PROCESSORS' in globals():
            for p in ACTIVE_JOB_PROCESSORS:
                try:
                    with p.task_queue.all_tasks_done:
                        p.task_queue.queue.clear()
                        p.task_queue.unfinished_tasks = 0
                        p.task_queue.all_tasks_done.notify_all()
                except Exception:
                    pass
            ACTIVE_JOB_PROCESSORS.clear()
    except Exception as e:
        print(f"Error during queue release: {e}")
        
    return jsonify({"status": "success", "message": "已发送停止指令，正在安全退出任务点..."})

@app.route("/api/status", methods=["GET"])
def get_status():
    with STATE_LOCK:
        # Get start index to only return incremental logs if requested
        last_index = request.args.get("last_index", default=0, type=int)
        
        all_logs = TASK_STATE["logs"]
        incremental_logs = all_logs[last_index:] if last_index < len(all_logs) else []
        
        return jsonify({
            "status": "success",
            "task_status": TASK_STATE["status"],
            "current_course": TASK_STATE["current_course"],
            "current_chapter": TASK_STATE["current_chapter"],
            "error_message": TASK_STATE["error_message"],
            "logs": incremental_logs,
            "next_index": len(all_logs)
        })

if __name__ == "__main__":
    print("*" * 40)
    print(" 学习通全自动刷课 Web 控制台启动中...")
    print(" 请在浏览器打开: http://127.0.0.1:5000")
    print("*" * 40)
    app.run(host="127.0.0.1", port=5000, debug=False)

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

#로그 데이터를 저장하는 리스트
audit_logs = []

#로그마다 고유한 번호를 주기 위해 사용하는 변수
next_log_id = 1

#로그 상태는 미리 정해진 값만 사용하도록 제한
status_list = ["미확인", "확인됨", "오탐"]

#상태에 따라 화면에 구분되도록 색상 매핑
color_list = ["#ffffff", "#ccffcc", "#ffcccc"]

def get_status_color(status):
    #현재 상태 값에 맞는 색상을 찾아서 반환
    return color_list[status_list.index(status)]

def refresh_listbox():
    #화면에 보이는 로그 목록을 데이터 기준으로 다시 그림
    listbox.delete(0, tk.END)

    for log in audit_logs:
        #로그 ID, 행동 유형, 상태를 한 줄로 표시
        listbox.insert(
            tk.END,
            f"[{log['log_id']}] {log['action_type']} ({log['status']})"
        )
        last_index = listbox.size() -1
        listbox.itemconfig(
            last_index,
            bg=get_status_color(log["status"])
        )

def get_selected_log():
    #현재 사용자가 선택한 로그를 데이터에서 찾아서 반환
    try:
        index = listbox.curselection()[0]
        return audit_logs[index]
    except IndexError:
        #아무것도 선택하지 않았을 경우
        return None
    
def create_log():
    #새로운 행동 로그를 생성하는 함수
    global next_log_id

    #사용자가 입력한 행동 유형
    action = entry_action.get().strip()
    #여러 줄 입력이 가능
    desc = text_desc.get("1.0", tk.END).strip()

    #필수 값이 비어 있으면 생성하지 않음
    if action == "" or desc == "":
        messagebox.showwarning("입력 오류", "행동 유형과 설명을 모두 입력하시오.")
        return
    
    #하나의 로그를 딕셔너리 형태로 구성
    log = {
        "log_id" : next_log_id,     #로그 고유 번호
        "action_type" : action,     #행동 유형
        "description" : desc,       #행동 상태
        "status" : "미확인",         #최초 상태
        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    #로그 목록에 추가
    audit_logs.append(log)
    next_log_id += 1

    #화면 목록을 데이터 기준으로 갱신
    refresh_listbox()

    #방금 추가한 로그를 자동으로 선택
    listbox.selection_set(tk.END)
    show_detail()

    #입력창 초기화
    entry_action.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)

def show_detail(event=None):
    #선택된 로그의 상세 정보를 화면에 표시
    log = get_selected_log()
    if not log:
        return
    
    #상태 정보 텍스트 구성
    detail_text.set(
        f"ID: {log['log_id']}\n"
        f"행동: {log['action_type']}\n"
        f"설명: {log['description']}\n"
        f"상태: {log['status']}\n"
        f"생성  : {log['created_at']}\n"
    )

    #상태에 따라 상세 영역 배경색 변경
    detail_label.config(bg=get_status_color(log["status"]))

def update_status():
    #로그의 내용은 유지하고 상태만 변경
    log = get_selected_log()
    if not log:
        messagebox.showwarning("선택오류", "수정할 로그를 선택하세요.")
        return
    
    #현재 상태의 다음 상태로 순환 변경
    current_index = status_list.index(log["status"])
    new_index = (current_index + 1) % len(status_list)

    log["status"] = status_list[new_index]

    print(f"[STATUS CHANGE] log_id={log['log_id']} -> {log['status']}")

    #변경된 상태를 화면에 즉시 반영
    refresh_listbox()
    show_detail()

def delete_log():
    #선택된 로그를 삭제
    log = get_selected_log()
    if not log:
        messagebox.showwarning("선택 오류", "삭제할 로그를 선택하세요.")
        return
    
    #실수 방지를 위해 삭제 확인
    if messagebox.askyesno("선택 확인", "정말 이 로그를 삭제하시겠습니까?"):
        audit_logs.remove(log)

    #목록과 상세 영역을 다시 갱신
    refresh_listbox()

    listbox.selection_clear(0, tk.END)

    detail_text.set("")
    detail_label.config(bg="#f0f0f0")

#프로그램 창 생성
root = tk.Tk()
root.title("AuditTrail - 사용자 행동 기록 관리 시스템")
root.geometry("800x400")

#왼쪽 영역 : 목록 로그
listbox = tk.Listbox(root, width=35)
listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

#목록 선택시 상세 정보 표시
listbox.bind("<<ListboxSelect>>", show_detail)

#가운데 영역 : 로그 상세 정보
detail_text = tk.StringVar()
detail_label = tk.Label(
    root,
    textvariable=detail_text,
    justify="left",
    anchor="nw",
    bg="#f0f0f0",
    width=40,
    height=15
)
detail_label.pack(side=tk.LEFT, padx=5, pady=5)

#오른쪽 영역 : 입력 및 버튼
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

tk.Label(right_frame, text="행동 유형").pack()
entry_action = tk.Entry(right_frame)
entry_action.pack(fill=tk.X)

tk.Label(right_frame, text="행동 설명").pack()
text_desc = tk.Text(right_frame, height=5)
text_desc.pack(fill=tk.X)

#CRUD버튼
tk.Button(right_frame, text="로그 생성", command=create_log).pack(fill=tk.X, pady=2)
tk.Button(right_frame, text="상태 변경", command=update_status).pack(fill=tk.X, pady=2)
tk.Button(right_frame, text="로그 삭제", command=delete_log).pack(fill=tk.X, pady=2)

#프로그램 실행
root.mainloop()
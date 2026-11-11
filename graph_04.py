# LangGraph 예제: 주간 회의 도우미
# 노드1: 입력 검증
# 노드2: 회의 정보 / 문구 생성
# 노드3: 회의록 요약
# 노드4: 규칙
# 노드5: 최종 Markdown 조합(내보내기)
# 내보내면 프론트가 받아서 화면에 표시


from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class MeetingState(TypedDict):
    title: str
    people: str
    notes: str
    error: str
    meeting_info: str
    summary: str
    actions: str
    result: str

def validate_input(state: MeetingState) -> MeetingState:
    title = (state.get("title") or "").strip()
    notes = (state.get("notes") or "").strip()
    if not title:
        return {**state, "error": "제목을 입력하세요."}
    if not notes:
        return {**state, "error": "회의록이 비어 있습니다."}
    return {**state, "error": ""}

def create_meeting(state: MeetingState) -> MeetingState:
    title = state["title"].strip()
    names = [p.strip() for p in (state.get("people") or "").split(",") if p.strip()]
    meeting_info = (f"### 회의 생성됨\n"
            f"- 제목: {title}\n"
            f"- 참가자: {','.join(names) or '(없음)'}")
    return {**state, "meeting_info": meeting_info}

def summarize_notes(state: MeetingState) -> MeetingState:
    lines = [ln.strip() for ln in state["notes"].splitlines() if ln.strip()]
    summary = f"발화 {len(lines)}줄 / 앞부분: {lines[0][:50] if lines else ''}"
    return {**state, "summary": summary}

def extract_actions(state: MeetingState) -> MeetingState:
    keywords = ("예정", "할", "todo", "해야", "담당")
    found = []
    for line in state["notes"].splitlines():
        text = line.strip()
        if text and any(k in text.lower() for k in keywords):
            found.append(f"- {text}")
    actions = "\n".join(found) if found else "- (추출된 액션 없음)"
    return {**state, "actions": actions}

def compose_result(state: MeetingState) -> MeetingState:
    if state.get("error"):
        return {**state, "result": f"### 오류\n{state['error']}"}
    result = (
        "### 회의 파이프라인 결과\n\n"
        f"1. 회의 정보\n{state['meeting_info']}\n\n"
        f"2. 요약\n{state['summary']}\n\n"
        f"3. 액션 아이템\n{state['actions']}"
    )
    return {**state, "result": result}

def route_after_validate(state: MeetingState) -> str:
    return "error" if state.get("error") else "ok"

def build_meeting_graph():
    graph = StateGraph(MeetingState)
    graph.add_node("validate", validate_input)
    graph.add_node("create_meeting", create_meeting)
    graph.add_node("summarize", summarize_notes)
    graph.add_node("extract_actions", extract_actions)
    graph.add_node("compose", compose_result)

    graph.add_edge(START, "validate")
    graph.add_conditional_edges(
        "validate", route_after_validate, {"ok": "create_meeting", "error": "compose"}
    )
    graph.add_edge("create_meeting", "summarize")
    graph.add_edge("summarize", "extract_actions")
    graph.add_edge("extract_actions", "compose")
    graph.add_edge("compose", END)
    return graph.compile()


meeting_app = build_meeting_graph()

def run_meeting_pipeline(title: str, people: str, notes: str) -> str:
    final_state = meeting_app.invoke(
        {
            "title": title, 
            "people": people, 
            "notes": notes, 
            "error": "", 
            "meeting_info": "",
            "summary": "",
            "actions": "",
            "result": ""
        }
    )
    return final_state["result"]






# # 내가 만든 거
# from typing import TypedDict
# from langgraph.graph import StateGraph, START, END

# from langchain_community.utilities import SQLDatabase

# # db = SQLDatabase.from_uri(f"sqlite:///{path.resolve().as_posix()}")

# schema = db.get_table_info(['Invoice', 'Customer', 'Employee'])

# class SQLState(TypedDict, total=False):
#     question: str
#     sql: str
#     result: str
#     answer: str
#     error: str

# # def generate_sql(state: SQLState):
# #     p = f"""다음 SQLite 스키마만 사용해 SELECT SQL 하나를 만드세요.
# #     코드블록 없이 SQL만 출력하고 LIMIT 10을 포함하세요.
# #     스키마: {schema}
# #     질문: {state['question']}"""
# #     return {"sql": llm.invoke(p).content}

# # def execute_sql(state: SQLState):
# #     try: 
# #         df = read_only_query(state['sql'], max_rows=10) # 함수에 sql을 넣어서 실행
# #         return {"result": df.to_json(orient='records', force_ascii=False), "error": ""} # json형태로 데이터프레임을 만들어 결과를 리턴
# #     except Exception as e:
# #         return {"result": "", "error": str(e)}

# # def make_answer(state: SQLState):
# #     # 데이터를 가져옴
# #     if state.get("error"): # 에러가 있다면
# #         return {"answer": "쿼리 실행 실패: " + state['error']}
# #     msg = f'질문: {state['question']}\n조회 결과: {state['result']}\n조회 결과에 근거하여 한국어로 답하세요'
# #     return {"answer": llm.invoke(msg).content}



# # LangGraph 예제: 주간 회의 도우미
# # 노드1: 입력 검증
# # 노드2: 회의 정보 / 문구 생성
# # 노드3: 회의록 요약
# # 노드4: 규칙
# # 노드5: 최종 Markdown 조합(내보내기)
# # 내보내면 프론트가 받아서 화면에 표시

# builder = StateGraph(SQLState)
# builder.add_node("입력 검증", input_val)
# builder.add_node("회의 정보", infor_meeting)
# builder.add_node("회의록 요약", sub_meeting)
# builder.add_node("규칙", rule)
# builder.add_node("최종 Markdown 조합(내보내기)", )

# builder.add_edge(START, "입력 검증")
# builder.add_edge("입력 검증", "회의 정보")
# builder.add_edge("회의 정보", "회의록 요약")
# builder.add_edge("회의록 요약", "규칙")
# builder.add_edge("규칙", "최종 Markdown 조합(내보내기)")
# builder.add_edge("최종 Markdown 조합(내보내기)", END)

# sql_graph = builder.compile()
# sql_graph
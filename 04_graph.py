# LangGraph 예제: 주간 회의 도우미
# 노드1: 입력 검증
# 노드2: 회의 정보 / 문구 생성
# 노드3: 회의록 요약
# 노드4: 규칙
# 노드5: 최종 Markdown 조합(내보내기)
# 내보내면 프론트가 받아서 화면에 표시


from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_community.utilities import SQLDatabase

# db = SQLDatabase.from_uri(f"sqlite:///{path.resolve().as_posix()}")

schema = db.get_table_info(['Invoice', 'Customer', 'Employee'])

class SQLState(TypedDict, total=False):
    question: str
    sql: str
    result: str
    answer: str
    error: str

# def generate_sql(state: SQLState):
#     p = f"""다음 SQLite 스키마만 사용해 SELECT SQL 하나를 만드세요.
#     코드블록 없이 SQL만 출력하고 LIMIT 10을 포함하세요.
#     스키마: {schema}
#     질문: {state['question']}"""
#     return {"sql": llm.invoke(p).content}

# def execute_sql(state: SQLState):
#     try: 
#         df = read_only_query(state['sql'], max_rows=10) # 함수에 sql을 넣어서 실행
#         return {"result": df.to_json(orient='records', force_ascii=False), "error": ""} # json형태로 데이터프레임을 만들어 결과를 리턴
#     except Exception as e:
#         return {"result": "", "error": str(e)}

# def make_answer(state: SQLState):
#     # 데이터를 가져옴
#     if state.get("error"): # 에러가 있다면
#         return {"answer": "쿼리 실행 실패: " + state['error']}
#     msg = f'질문: {state['question']}\n조회 결과: {state['result']}\n조회 결과에 근거하여 한국어로 답하세요'
#     return {"answer": llm.invoke(msg).content}



# LangGraph 예제: 주간 회의 도우미
# 노드1: 입력 검증
# 노드2: 회의 정보 / 문구 생성
# 노드3: 회의록 요약
# 노드4: 규칙
# 노드5: 최종 Markdown 조합(내보내기)
# 내보내면 프론트가 받아서 화면에 표시

builder = StateGraph(SQLState)
builder.add_node("입력 검증", input_val)
builder.add_node("회의 정보", infor_meeting)
builder.add_node("회의록 요약", sub_meeting)
builder.add_node("규칙", rule)
builder.add_node("최종 Markdown 조합(내보내기)", )

builder.add_edge(START, "입력 검증")
builder.add_edge("입력 검증", "회의 정보")
builder.add_edge("회의 정보", "회의록 요약")
builder.add_edge("회의록 요약", "규칙")
builder.add_edge("규칙", "최종 Markdown 조합(내보내기)")
builder.add_edge("최종 Markdown 조합(내보내기)", END)

sql_graph = builder.compile()
sql_graph
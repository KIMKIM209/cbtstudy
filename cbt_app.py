# -*- coding: utf-8 -*-
import streamlit as st
import importlib

# 페이지 기본 설정
st.set_page_config(page_title="국가기술자격 실전 CBT", page_icon="⚡", layout="centered")

st.title("⚡ 전기기능사 기출문제 연습")

# 1. 23개년부틔 25개년까지의 전체 기출문제 동적 매핑 정의
exam_mapping = {
    "25년도 1회차 시험 (202501)": "questions202501",
    "25년도 2회차 시험 (202502)": "questions202502",
    "25년도 3회차 시험 (202503)": "questions202503",
    "24년도 1회차 시험 (202401)": "questions202401",
    "24년도 2회차 시험 (202402)": "questions202402",
    "24년도 3회차 시험 (202403)": "questions202403",
    "23년도 1회차 시험 (202301)": "questions202301",
    "23년도 2회차 시험 (202302)": "questions202302",
    "23년도 3회차 시험 (202303)": "questions202303"
}

# 상단 선택 상자 구성
exam_choice = st.selectbox(
    "📝 응시할 기출문제를 선택하세요:",
    list(exam_mapping.keys())
)

# 선택된 회차에 해당하는 파일명 매칭
selected_module_name = exam_mapping[exam_choice]

# 2. 회차 전환 시 메모리 엉킴 차단 및 세션 초기화 로직
if 'current_exam' not in st.session_state:
    st.session_state.current_exam = selected_module_name

if selected_module_name != st.session_state.current_exam:
    st.session_state.current_exam = selected_module_name
    st.session_state.user_answers = {}
    st.session_state.submitted = False
    st.rerun()

if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 3. 실시간 동적 모듈 로드 엔진
try:
    exam_module = importlib.import_module(selected_module_name)
    questions = exam_module.questions
except ImportError:
    st.error(f"⚠️ '{selected_module_name}.py' 데이터 파일이 폴더에 존재하지 않습니다. 파일을 준비해 주세요.")
    st.stop()

st.write(f"현재 선택: **{exam_choice}** (총 {len(questions)}문항 배치 완료)")

# 4. 문제 풀이 레이아웃
for idx, item in enumerate(questions):
    st.markdown("---")
    st.subheader(f"Q{item['num']}. {item['q']}")
    
    choice = st.radio(
        "보기 선택:", 
        item['options'], 
        key=f"q_{selected_module_name}_{idx}", # 회차별 고유 세션 키 바인딩
        index=None,
        disabled=st.session_state.submitted 
    )
    st.session_state.user_answers[idx] = choice

st.markdown("---")

# 5. 채점 및 결과 분석 시스템
if not st.session_state.submitted:
    if st.button("🏁 시험 종료 및 채점하기", type="primary"):
        st.session_state.submitted = True
        st.rerun()
else:
    correct_count = 0
    wrong_questions = []
    correct_questions = []

    for idx, item in enumerate(questions):
        my_answer = st.session_state.user_answers.get(idx)
        if my_answer == item['answer']:
            correct_count += 1
            correct_questions.append({"item": item, "my_answer": my_answer})
        else:
            wrong_questions.append({"item": item, "my_answer": my_answer})

    score = int((correct_count / len(questions)) * 100)
    
    st.header("📊 최종 채점 결과")
    col1, col2, col3 = st.columns(3)
    col1.metric("내 점수", f"{score}점")
    col2.metric("맞은 문제", f"{correct_count}개")
    col3.metric("틀린 문제", f"{len(wrong_questions)}개")

    if score >= 60:
        st.success("🎉 합격 기준을 안정적으로 충족했습니다! 이 견고한 흐름을 이어가세요.")
    else:
        st.warning("⚠️ 보완이 필요한 구간입니다. 아래 오답 분석 탭에 에너지를 집중하세요.")

    tab1, tab2 = st.tabs(["📝 틀린 문제 (오답 노트)", "✅ 맞은 문제 다시보기"])
    
    with tab1:
        if wrong_questions:
            for wrong in wrong_questions:
                item = wrong["item"]
                my_ans = wrong["my_answer"]
                with st.expander(f"Q{item['num']} 오답 분석"):
                    st.write(f"**문제:** {item['q']}")
                    st.error(f"내 선택: {my_ans if my_ans else '미선택'}")
                    st.success(f"정답: {item['answer']}")
                    st.info(f"💡 해설: {item['explanation']}")
        else:
            st.success("완벽합니다. 틀린 문항이 단 하나도 없습니다.")

    with tab2:
        if correct_questions:
            for correct in correct_questions:
                item = correct["item"]
                my_ans = correct["my_answer"]
                with st.expander(f"Q{item['num']} 정답 확인"):
                    st.write(f"**문제:** {item['q']}")
                    st.success(f"내 선택 & 정답: {my_ans}")
                    st.info(f"💡 해설: {item['explanation']}")
                    
    st.markdown("---")
    if st.button("🔄 현재 회차 처음부터 다시 풀기"):
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        st.rerun()

# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import math

# 화면을 넓게 쓰는 실전형 와이드 레이아웃
st.set_page_config(page_title="국가기술자격 실전 CBT", page_icon="⚡", layout="wide")

st.title("⚡ 전기기능사 실전 CBT")

# 1. 기출문제 동적 매핑
exam_mapping = {
    "25년도 1회차 시험 (202501)": "questions202501",
    "25년도 2회차 시험 (202502)": "questions202502",
    "25년도 3회차 시험 (202503)": "questions202503",
    "24년도 1회차 시험 (202401)": "questions202401",
    "24년도 2회차 시험 (202402)": "questions202402",
    "24년도 3회차 시험 (202403)": "questions202403",
    "23년도 1회차 시험 (202301)": "questions202301",
    "23년도 2회차 시험 (202302)": "questions202302",
    "23년도 3회차 시험 (202303)": "questions202303",
    "26년도 꼼수 63문제": "questions"
}

exam_list = list(exam_mapping.keys())

# 2. 전역 세션 상태 및 페이지네이션 메모리 통제
if 'selected_exam_name' not in st.session_state:
    st.session_state.selected_exam_name = exam_list[0]
    st.session_state.current_exam = exam_mapping[exam_list[0]]

if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# 상단 메뉴
exam_choice = st.selectbox(
    "📝 응시할 기출문제를 선택하세요:",
    exam_list,
    index=exam_list.index(st.session_state.selected_exam_name)
)

if exam_choice != st.session_state.selected_exam_name:
    st.session_state.selected_exam_name = exam_choice
    st.session_state.current_exam = exam_mapping[exam_choice]
    st.session_state.user_answers = {}
    st.session_state.submitted = False
    st.session_state.current_page = 1
    st.rerun()

selected_module_name = st.session_state.current_exam

# 3. 실시간 동적 모듈 로드 엔진
try:
    exam_module = importlib.import_module(selected_module_name)
    questions = exam_module.questions
except ImportError:
    st.error(f"⚠️ '{selected_module_name}.py' 데이터 파일이 폴더에 존재하지 않습니다.")
    st.stop()

# 페이지당 문항 수 고정 및 전체 페이지 계산
QUESTIONS_PER_PAGE = 6
total_pages = math.ceil(len(questions) / QUESTIONS_PER_PAGE)

# 4. 우측 고정형 실시간 OMR 사이드바 및 흐름 제어 스위치
with st.sidebar:
    st.header("📝 OMR 답안지")
    st.caption("문제를 풀면 실시간으로 마킹됩니다.")
    st.markdown("---")
    
    omr_col1, omr_col2 = st.columns(2)
    for idx, item in enumerate(questions):
        ans = st.session_state.user_answers.get(idx)
        ans_marker = ans[0] if ans else "표기 안됨"
        
        target_col = omr_col1 if idx % 2 == 0 else omr_col2
        target_col.markdown(f"**{item['num']}**. {ans_marker}")
        
    st.markdown("---")
    
    if not st.session_state.submitted:
        if st.button("🏁 최종 답안 제출", type="primary", use_container_width=True):
            st.session_state.submitted = True
            st.session_state.current_page = 1
            st.rerun()
    else:
        st.subheader("🔄 다음 단계 진행")
        next_choice = st.selectbox(
            "현재 회차 복습 또는 다른 회차 선택:", 
            exam_list, 
            index=exam_list.index(st.session_state.selected_exam_name),
            key="post_exam_selector"
        )
        if st.button("🚀 선택한 시험 시작", type="primary", use_container_width=True):
            st.session_state.selected_exam_name = next_choice
            st.session_state.current_exam = exam_mapping[next_choice]
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.current_page = 1
            st.rerun()

# 5. 본문 문제 풀이 영역 (제출 전)
if not st.session_state.submitted:
    st.write(f"현재 선택: **{st.session_state.selected_exam_name}** (총 {len(questions)}문항 / {total_pages}페이지)")
    st.progress(st.session_state.current_page / total_pages)
    st.markdown("---")
    
    start_idx = (st.session_state.current_page - 1) * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, len(questions))
    page_questions = questions[start_idx:end_idx]
    
    col_left, col_right = st.columns(2, gap="large")
    midpoint = math.ceil(len(page_questions) / 2)

    for i, item in enumerate(page_questions):
        actual_idx = start_idx + i 
        target_col = col_left if i < midpoint else col_right
        
        with target_col:
            st.markdown(f"**{item['num']}. {item['q']}**")
            
            # 💡 [핵심 교정부] 이미지를 화면 폭에 맞추지 않고 400픽셀로 고정하여 출력합니다.
            if item.get("image"):
                try:
                    st.image(item["image"], width=400)
                except Exception:
                    pass
            
            ans = st.session_state.user_answers.get(actual_idx)
            try:
                ans_index = item['options'].index(ans) if ans else None
            except ValueError:
                ans_index = None

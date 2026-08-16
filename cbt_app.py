# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import math
import re
import time
import datetime

# --- 1. 기본 설정 및 실전 CBT 전용 CSS ---
# 사이드바를 숨기고 넓은 화면을 강제하여 실전 몰입도를 극대화합니다.
st.set_page_config(page_title="국가기술자격 실전 CBT", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    header[data-testid="stHeader"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    .cbt-banner {
        background-color: #f0f4f8; border-top: 4px solid #0056b3; border-bottom: 2px solid #0056b3;
        padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
    }
    .cbt-banner .title { font-size: 24px; font-weight: 900; color: #0056b3; margin: 0; letter-spacing: -1px;}
    .cbt-banner .info { font-size: 16px; font-weight: 600; color: #333; margin: 0; line-height: 1.5;}
    .cbt-timer { font-size: 16px; font-weight: 700; color: #d9534f; margin: 0; line-height: 1.5; text-align: right;}
    
    .omr-header { background-color: #4a7ebb; color: white; text-align: center; padding: 10px; font-size: 16px; font-weight: bold; margin-bottom: 0px;}
    .omr-container { border: 1px solid #ddd; border-top: none; padding: 15px; height: 650px; overflow-y: auto; background-color: #fafafa;}
    .bottom-bar { margin-top: 20px; padding-top: 15px; border-top: 2px solid #ddd;}
    
    /* 보기 라디오 버튼 간격 최적화 */
    .stRadio > div { gap: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. 기출문제 데이터베이스 매핑 ---
exam_mapping = {
    "26년도 소방설비기사(전기) 2회차 시험 (202602)": "2602", 
    "26년도 소방설비기사(전기) 1회차 시험 (202601)": "2601", 
    "25년도 다산 소방설비기사(전기) 3회차 시험 (202503)": "D2503", 
    "25년도 다산 소방설비기사(전기) 2회차 시험 (202502)": "D2502",     
    "25년도 다산 소방설비기사(전기) 1회차 시험 (202501)": "D2501", 
    "24년도 다산 소방설비기사(전기) 3회차 시험 (202403)": "D2403",
    "24년도 다산 소방설비기사(전기) 2회차 시험 (202402)": "D2402",
    "24년도 다산 소방설비기사(전기) 1회차 시험 (202401)": "D2401",
    "23년도 소방설비기사(전기) 4회차 시험 (202304)": "D2304",
    "23년도 소방설비기사(전기) 2회차 시험 (202302)": "D2302",
    "23년도 소방설비기사(전기) 1회차 시험 (202301)": "D23011", 
    "22년도 소방설비기사(전기) 4회차 시험 (202204)": "D2204",
    "22년도 소방설비기사(전기) 2회차 시험 (202202)": "D2202",
    "22년도 소방설비기사(전기) 1회차 시험 (202201)": "D2201", 
    "25년도 소방설비기사(전기) 3회차 시험 (202501)": "2503", 
    "25년도 소방설비기사(전기) 2회차 시험 (202501)": "2502",     
    "25년도 소방설비기사(전기) 1회차 시험 (202501)": "2501", 
    "26년도 전기기능사 2회차 시험 (202602)": "questions202602",
    "26년도 전기기능사 1회차 시험 (202601)": "questions202601",
    "25년도 전기기능사 1회차 시험 (202501)": "questions202501",
    "25년도 전기기능사 2회차 시험 (202502)": "questions202502",
    "25년도 전기기능사 3회차 시험 (202503)": "questions202503",
    "26년도 기본 90제": "questions90",  
    "26년도 꼼수 63문제": "questions"
}
exam_list = list(exam_mapping.keys())

# --- 3. 전역 세션 상태 통제 ---
if 'selected_exam_name' not in st.session_state:
    st.session_state.selected_exam_name = exam_list[0]
    st.session_state.current_exam = exam_mapping[exam_list[0]]
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'img_expanded' not in st.session_state:
    st.session_state.img_expanded = False

# (인터페이스 설정 모드 - 실전 UI를 해치지 않도록 숨김 처리)
with st.expander("⚙️ 시험 선택 및 설정 (클릭하여 열기)"):
    col_set1, col_set2 = st.columns([3, 1])
    with col_set1:
        exam_choice = st.selectbox("📝 응시할 기출문제를 선택하세요:", exam_list, index=exam_list.index(st.session_state.selected_exam_name))
    with col_set2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.toggle("🔍 그림 크게 보기", key="img_expanded")
        
    if exam_choice != st.session_state.selected_exam_name:
        st.session_state.selected_exam_name = exam_choice
        st.session_state.current_exam = exam_mapping[exam_choice]
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        st.session_state.current_page = 1
        st.session_state.start_time = time.time()
        st.session_state.end_time = None
        st.rerun()

# --- 4. 데이터 로드 및 환경 변수 계산 ---
selected_module_name = st.session_state.current_exam
try:
    exam_module = importlib.import_module(selected_module_name)
    questions = exam_module.questions
except ImportError:
    st.error(f"⚠️ '{selected_module_name}.py' 파일이 존재하지 않습니다.")
    st.stop()

QUESTIONS_PER_PAGE = 5
total_pages = math.ceil(len(questions) / QUESTIONS_PER_PAGE)
limit_minutes = int(len(questions) * 1.5) if len(questions) >= 80 else len(questions)
current_img_width = 450 if st.session_state.img_expanded else 250

# --- 5. 화면 렌더링 (제출 전 / 실전 CBT 모드) ---
if not st.session_state.submitted:
    elapsed_seconds = int(time.time() - st.session_state.start_time)
    remain_seconds = max((limit_minutes * 60) - elapsed_seconds, 0)
    remain_td = datetime.timedelta(seconds=remain_seconds)
    
    # [상단 CBT 배너]
    st.markdown(f"""
    <div class="cbt-banner">
        <div class="title">자격검정 CBT 웹체험 문제풀이</div>
        <div class="info">
            수험번호 : <span style="color:#0056b3;">00000000</span><br>
            수험자명 : <span style="color:#0056b3;">김영준 (수험자)</span>
        </div>
        <div class="cbt-timer">
            ⏱️ 제한 시간 : {limit_minutes}분<br>
            남은 시간 : {remain_td}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # [핵심] 메인 레이아웃 분할 (좌측 문제 7.5 : 우측 OMR 2.5)
    col_main, col_omr = st.columns([7.5, 2.5], gap="large")
    
    with col_main:
        # 좌측 문제 풀이 영역
        start_idx = (st.session_state.current_page - 1) * QUESTIONS_PER_PAGE
        end_idx = min(start_idx + QUESTIONS_PER_PAGE, len(questions))
        page_questions = questions[start_idx:end_idx]
        
        for i, item in enumerate(page_questions):
            actual_idx = start_idx + i 
            
            st.markdown(f"**{item['num']}. {item['q']}**")
            
            if item.get("image"):
                try:
                    st.image(item["image"], width=current_img_width)
                except Exception:
                    pass
            
            ans = st.session_state.user_answers.get(actual_idx)
            try:
                ans_index = item['options'].index(ans) if ans else None
            except ValueError:
                ans_index = None
            
            choice = st.radio(
                label="보기 선택", 
                options=item['options'], 
                key=f"q_{actual_idx}", 
                index=ans_index,
                label_visibility="collapsed" 
            )
            st.session_state.user_answers[actual_idx] = choice
            st.markdown("---")
            
        # 하단 네비게이션 컨트롤
        st.markdown("<div class='bottom-bar'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 2.5, 1.5, 2])
        
        with btn_col1:
            st.button("🧮 계산기", disabled=True, use_container_width=True)
        with btn_col2:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>{st.session_state.current_page} / {total_pages} 페이지</b></div>", unsafe_allow_html=True)
        with btn_col3:
            if st.session_state.current_page < total_pages:
                if st.button("다음 ▶", use_container_width=True):
                    st.session_state.current_page += 1
                    st.rerun()
            elif st.session_state.current_page > 1:
                if st.button("◀ 이전", use_container_width=True):
                    st.session_state.current_page -= 1
                    st.rerun()
        with btn_col4:
            if st.button("✅ 답안 제출", type="primary", use_container_width=True):
                st.session_state.submitted = True
                st.session_state.end_time = time.time()
                st.rerun()

    with col_omr:
        # 우측 OMR 답안 현황판 (클릭 시 빠른 이동)
        st.markdown("<div class='omr-header'>답안 표기란 (클릭 시 이동)</div>", unsafe_allow_html=True)
        
        with st.container(height=650):
            cols = st.columns(4)
            for idx in range(len(questions)):
                q_num = idx + 1
                is_answered = st.session_state.user_answers.get(idx) is not None
                
                # 마킹 시 초록색, 미마킹 시 회색 원 표시
                btn_label = f"🟢 {q_num}" if is_answered else f"⚪ {q_num}"
                col_idx = idx % 4
                
                if cols[col_idx].button(btn_label, key=f"omr_btn_{idx}", use_container_width=True):
                    st.session_state.current_page = (idx // QUESTIONS_PER_PAGE) + 1
                    st.rerun()

# --- 6. 화면 렌더링 (제출 후 / 결과 분석 모드) ---
else:
    st.markdown(f"### 📊 채점 결과 : {st.session_state.selected_exam_name}")
    
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

    total_score = int((correct_count / len(questions)) * 100)
    
    total_seconds = int(st.session_state.end_time - st.session_state.start_time)
    taken_minutes, taken_seconds = divmod(total_seconds, 60)
    
    st.info(f"⏱️ **소요 시간:** {taken_minutes}분 {taken_seconds}초 / 제한 {limit_minutes}분")
    
    # 합불 판정 분기 (기사급 80~100문항 과락 로직)
    if len(questions) in [80, 100]:
        num_subjects = len(questions) // 20
        subject_scores = []
        is_fail_by_subject = False
        
        for i in range(num_subjects):
            sub_start = i * 20
            sub_end = sub_start + 20
            sub_correct = sum(1 for j in range(sub_start, sub_end) if st.session_state.user_answers.get(j) == questions[j]['answer'])
            sub_score = sub_correct * 5 
            subject_scores.append(sub_score)
            if sub_score < 40:
                is_fail_by_subject = True

        avg_score = sum(subject_scores) / num_subjects
        
        col_tot1, col_tot2, col_tot3, col_tot4 = st.columns(4)
        col_tot1.metric("총 평균 점수", f"{avg_score:.1f}점")
        col_tot2.metric("맞은 문제", f"{correct_count}개")
        col_tot3.metric("틀린 문제", f"{len(wrong_questions)}개")
        
        if avg_score >= 60 and not is_fail_by_subject:
            col_tot4.metric("최종 결과", "🟢 합격")
            st.success("🎉 합격입니다! 과락 방어 및 평균 점수를 달성했습니다.")
        else:
            col_tot4.metric("최종 결과", "🔴 불합격")
            if is_fail_by_subject:
                st.error("⚠️ 과락 발생: 40점 미만인 과목이 존재합니다.")
            else:
                st.warning("⚠️ 점수 미달: 과락은 없으나 전체 평균 60점에 도달하지 못했습니다.")

        st.markdown("##### 📌 과목별 상세 (과락: 40점 미만)")
        sub_cols = st.columns(num_subjects)
        for i in range(num_subjects):
            sub_status = "🔴 과락" if subject_scores[i] < 40 else "🟢 통과"
            sub_cols[i].metric(f"제 {i+1}과목", f"{subject_scores[i]}점", sub_status, delta_color="off" if subject_scores[i] >= 40 else "inverse")

    # (기능사급 60문항 과락 없음 로직)
    elif len(questions) == 60:
        subject_scores = []
        for i in range(3):
            sub_start = i * 20
            sub_end = sub_start + 20
            sub_correct = sum(1 for j in range(sub_start, sub_end) if st.session_state.user_answers.get(j) == questions[j]['answer'])
            sub_score = sub_correct * 5 
            subject_scores.append(sub_score)

        col_tot1, col_tot2, col_tot3, col_tot4 = st.columns(4)
        col_tot1.metric("총 점수", f"{total_score}점")
        col_tot2.metric("맞은 문제", f"{correct_count}개")
        col_tot3.metric("틀린 문제", f"{len(wrong_questions)}개")
        
        if total_score >= 60:
            col_tot4.metric("최종 결과", "🟢 합격")
        else:
            col_tot4.metric("최종 결과", "🔴 불합격")

        st.markdown("##### 📌 과목별 상세 (기능사 과락 없음)")
        sub_cols = st.columns(3)
        for i in range(3):
            sub_cols[i].metric(f"제 {i+1}과목", f"{subject_scores[i]}점")

    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("내 점수", f"{total_score}점")
        col2.metric("맞은 문제", f"{correct_count}개")
        col3.metric("틀린 문제", f"{len(wrong_questions)}개")

    if st.button("🔄 메인으로 돌아가기 (초기화)", type="primary"):
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        st.session_state.current_page = 1
        st.session_state.start_time = time.time()
        st.session_state.end_time = None
        st.rerun()

    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 틀린 문제 (오답 노트)", "✅ 맞은 문제 다시보기"])
    
    tab_img_width = 400 if st.session_state.img_expanded else 250
    
    with tab1:
        if wrong_questions:
            for wrong in wrong_questions:
                item = wrong["item"]
                my_ans = wrong["my_answer"]
                with st.expander(f"Q{item['num']} 오답 분석"):
                    st.write(f"**문제:** {item['q']}")
                    if item.get("image"):
                        try: st.image(item["image"], width=tab_img_width)
                        except Exception: pass
                    st.error(f"내 선택: {my_ans if my_ans else '미선택'}")
                    st.success(f"정답: {item['answer']}")
                    st.info(f"💡 해설: {item['explanation']}")
        else:
            st.success("완벽합니다. 오답이 존재하지 않습니다.")

    with tab2:
        if correct_questions:
            for correct in correct_questions:
                item = correct["item"]
                my_ans = correct["my_answer"]
                with st.expander(f"Q{item['num']} 정답 확인"):
                    st.write(f"**문제:** {item['q']}")
                    if item.get("image"):
                        try: st.image(item["image"], width=tab_img_width)
                        except Exception: pass
                    st.success(f"내 선택 & 정답: {my_ans}")
                    st.info(f"💡 해설: {item['explanation']}")

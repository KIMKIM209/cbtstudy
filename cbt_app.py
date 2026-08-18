# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import math
import re
import time
import datetime

# =====================================================================
# 0. 보안 설정 (아이디/비밀번호 및 기간 설정)
# =====================================================================
# 👑 관리자 계정 (본인 전용, 무제한 접속)
ADMIN_ID = "kims"
ADMIN_PW = "880801"

# 🤝 게스트 계정 (지인 공유용, 기간 한정 접속)
GUEST_ID = "free"
GUEST_PW = "1004"
GUEST_EXPIRY_DATE = "2026-08-16" # YYYY-MM-DD 형식으로 만료일 지정

# --- 1. 기본 설정 및 실전 CBT 전용 CSS ---
st.set_page_config(page_title="국가기술자격 실전 CBT", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* =====================================================================
       💡 폰트 및 시각 환경 실전 완벽 동기화 (CBT 표준 질감)
       ===================================================================== */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown li,
    div[role="radiogroup"] label p, div[role="radiogroup"] label div,
    .stButton button p,
    summary p,
    .cbt-banner, .cbt-banner div, .cbt-banner span,
    .omr-header, .omr-num, .omr-dots span, .omr-row, .omr-subject-header,
    .review-info-header, .review-info-body, .review-info-body b,
    .result-banner, .result-table th, .result-table td,
    .study-correct {
        font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', '굴림', 'Apple SD Gothic Neo', sans-serif !important;
        letter-spacing: -0.5px !important;
        word-break: keep-all !important;
    }

    /* 기본 UI 숨김 */
    header[data-testid="stHeader"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    /* 상단 배너 */
    .cbt-banner {
        background-color: #00a2e8; color: white;
        padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
    }
    .cbt-banner .title { font-size: 24px; font-weight: 900; margin: 0; letter-spacing: -1px !important;}
    .cbt-banner .info { font-size: 15px; font-weight: 600; text-align: right; line-height: 1.4;}
    
    /* 우측 OMR 패널 (풀이 화면용) */
    .omr-header { background-color: #4a7ebb; color: white; text-align: center; padding: 10px; font-size: 16px; font-weight: bold; margin-bottom: 0px;}
    .bottom-bar { margin-top: 20px; padding-top: 15px; border-top: 2px solid #ddd;}
    
    /* 리뷰 화면 (제출 전 확인) CSS */
    .review-container { display: flex; gap: 15px; margin-top: 10px; }
    .review-info-panel { flex: 1.5; border: 2px solid #ddd; background: #fff; height: fit-content; }
    .review-info-header { background: #008CBA; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 18px; }
    .review-info-body { padding: 20px; font-size: 14px; line-height: 2.2; }
    
    .review-omr-panel { flex: 8.5; border: 2px solid #4a7ebb; background: #fff; }
    .review-omr-header { background: #4a7ebb; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 18px; }
    
    /* 리뷰 화면 OMR 20문제 단위 컬럼 그리드 */
    .omr-review-grid { display: grid; gap: 5px; padding: 10px; background: #f9f9f9;}
    .omr-col { display: flex; flex-direction: column; background: #fff; border: 1px solid #ddd; }
    .omr-subject-header { background: #5b9bd5; color: white; text-align: center; font-weight: bold; padding: 8px 0; font-size: 14px; margin-bottom: 5px;}
    .omr-row { display: flex; align-items: center; justify-content: center; gap: 15px; padding: 4px 10px; font-size: 15px; border-bottom: 1px dashed #eee;}
    .omr-row:last-child { border-bottom: none; }
    
    /* 미마킹 강조 (노란색 배경) */
    .omr-row.unanswered { background-color: #ffe699; font-weight: bold; border: 1px solid #ff4b4b;}
    
    .omr-num { color: #d9534f; width: 25px; font-weight: bold; text-align: center;}
    .omr-dots { display: flex; gap: 8px; }
    
    /* 최종 결과 화면 CSS */
    .result-banner { padding: 30px; text-align: center; color: white; margin-bottom: 20px; font-size: 26px; font-weight: bold; border-radius: 5px; }
    .result-pass { background-color: #0078d7; } 
    .result-fail { background-color: #d9534f; } 
    .result-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 16px; text-align: center; }
    .result-table th { background-color: #f2f2f2; border: 1px solid #ddd; padding: 12px; font-weight: bold; }
    .result-table td { border: 1px solid #ddd; padding: 12px; }
    
    /* 합격/불합격 폰트 2배 확장 */
    .result-score-pass { color: #0078d7; font-weight: 900; font-size: 48px; }
    .result-score-fail { color: #d9534f; font-weight: 900; font-size: 48px; }
    
    /* 보기 라디오 버튼 간격 */
    .stRadio > div { gap: 10px; }
    
    /* 학습 모드 전용 */
    .study-correct { color: #0078d7; font-weight: bold; background-color: #e6f2ff; padding: 4px 8px; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 0. 접근 통제 (Gatekeeper) 로직
# =====================================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #0056b3;'>🔒 시스템 접근 인증</h2>", unsafe_allow_html=True)
        st.info("지적 자산 보호 및 권한 없는 접근을 통제하기 위해 계정 인증이 필요합니다.")
        
        with st.form("login_form"):
            input_id = st.text_input("아이디 (ID)")
            input_pw = st.text_input("비밀번호 (Password)", type="password")
            submit_btn = st.form_submit_button("접속하기 (Login)", use_container_width=True)
            
            if submit_btn:
                today_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                if input_id == ADMIN_ID and input_pw == ADMIN_PW:
                    st.session_state.authenticated = True
                    st.session_state.user_type = "Admin"
                    st.rerun()
                elif input_id == GUEST_ID and input_pw == GUEST_PW:
                    if today_date <= GUEST_EXPIRY_DATE:
                        st.session_state.authenticated = True
                        st.session_state.user_type = "Guest"
                        st.rerun()
                    else:
                        st.error(f"🚨 해당 계정의 접속 승인 기한({GUEST_EXPIRY_DATE})이 만료되었습니다. 관리자에게 문의하세요.")
                else:
                    st.error("🚨 인증 정보가 일치하지 않습니다. 정확히 입력해 주세요.")
    st.stop()


# --- 2. 전체 기출문제 원본 매핑 ---
ALL_EXAM_MAPPING = {
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

# 🔒 [접근 제어] 게스트 계정 접속 시 '소방설비기사' 제외 필터링
if st.session_state.user_type == "Guest":
    exam_mapping = {k: v for k, v in ALL_EXAM_MAPPING.items() if "소방설비기사" not in k}
else:
    exam_mapping = ALL_EXAM_MAPPING

exam_list = list(exam_mapping.keys())

# --- 3. 전역 세션 상태 통제 ---
# 세션에 저장된 시험명이 현재 권한 목록(exam_list)에 없는 경우 첫 번째 시험으로 자동 재설정
if ('selected_exam_name' not in st.session_state) or (st.session_state.selected_exam_name not in exam_list):
    st.session_state.selected_exam_name = exam_list[0]
    st.session_state.current_exam = exam_mapping[exam_list[0]]

if 'current_exam' not in st.session_state: st.session_state.current_exam = exam_mapping[st.session_state.selected_exam_name]
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'review_mode' not in st.session_state: st.session_state.review_mode = False 
if 'submitted' not in st.session_state: st.session_state.submitted = False 
if 'study_mode' not in st.session_state: st.session_state.study_mode = False 
if 'current_page' not in st.session_state: st.session_state.current_page = 1
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
if 'end_time' not in st.session_state: st.session_state.end_time = None
if 'img_expanded' not in st.session_state: st.session_state.img_expanded = False
if 'wrong_history' not in st.session_state: st.session_state.wrong_history = set()

# 💡 실전(시험) 모드용 레이아웃 및 폰트 설정 상태 변수 초기화
if 'font_exam' not in st.session_state: st.session_state.font_exam = "100%"
if 'layout_exam' not in st.session_state: st.session_state.layout_exam = "가로(1단)"

with st.expander("⚙️ 시험 선택 및 설정 (초기화)"):
    col_set1, col_set2 = st.columns([3, 1])
    with col_set1:
        exam_choice = st.selectbox("📝 응시할 기출문제:", exam_list, index=exam_list.index(st.session_state.selected_exam_name))
    with col_set2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.toggle("🔍 그림 크게 보기", key="img_expanded")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📖 정답/해설 보며 공부하기 (학습 모드)", use_container_width=True):
            st.session_state.study_mode = True
            st.session_state.review_mode = False
            st.session_state.submitted = False
            st.rerun()
            
    if exam_choice != st.session_state.selected_exam_name:
        st.session_state.selected_exam_name = exam_choice
        st.session_state.current_exam = exam_mapping[exam_choice]
        st.session_state.user_answers = {}
        st.session_state.review_mode = False
        st.session_state.submitted = False
        st.session_state.study_mode = False
        st.session_state.current_page = 1
        st.session_state.start_time = time.time()
        st.session_state.end_time = None
        st.rerun()

# --- 4. 데이터 로드 ---
selected_module_name = st.session_state.current_exam
try:
    exam_module = importlib.import_module(selected_module_name)
    questions = exam_module.questions
except ImportError:
    st.error(f"⚠️ '{selected_module_name}.py' 파일이 존재하지 않습니다.")
    st.stop()

current_img_width = 450 if st.session_state.img_expanded else 250

elapsed_seconds = int(time.time() - st.session_state.start_time)
if st.session_state.end_time:
    elapsed_seconds = int(st.session_state.end_time - st.session_state.start_time)
remain_seconds = max((int(len(questions) * 1.5) if len(questions) >= 80 else len(questions)) * 60 - elapsed_seconds, 0)
remain_td = datetime.timedelta(seconds=remain_seconds)
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# 접속자 이름 및 게스트 전용 기한 표시 로직
display_user_name = "홍길동" if st.session_state.user_type == "Admin" else "게스트 (Guest)"
guest_expiry_banner = f"<span style='color: #ffeb3b;'>사용기간 : ~ {GUEST_EXPIRY_DATE}</span><br>" if st.session_state.user_type == "Guest" else ""
guest_expiry_review = f"<b>사용기간:</b> ~ <span style='color: #d9534f;'>{GUEST_EXPIRY_DATE}</span><br><br>" if st.session_state.user_type == "Guest" else ""


# =====================================================================
# 5. [STEP 0] 학습 모드 (Study Mode - 순수 리스트 뷰 및 인쇄)
# =====================================================================
if st.session_state.study_mode:
    st.markdown(f"### 📖 학습 모드 : {st.session_state.selected_exam_name}")
    st.info("💡 이 모드에서는 전체 문항의 정답과 해설을 즉시 확인하며 빠르게 회독할 수 있습니다.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🖨️ 인쇄하기", use_container_width=True):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)
    with col_s2:
        if st.button("↩️ 실전 모드로 돌아가기 (초기화)", type="primary", use_container_width=True):
            st.session_state.study_mode = False
            st.session_state.user_answers = {}
            st.session_state.current_page = 1
            st.session_state.start_time = time.time()
            st.rerun()
            
    st.markdown("---")
    
    for item in questions:
        st.markdown(f"**{item['num']}. {item['q']}**")
        if item.get("image"):
            try: st.image(item["image"], width=current_img_width)
            except Exception: pass
            
        for opt in item['options']:
            if opt == item['answer']:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span class='study-correct'>{opt}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span style='color:#777;'>{opt}</span>", unsafe_allow_html=True)
                
        st.success(f"💡 해설: {item['explanation']}")
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <style>
        @media print {
            header[data-testid="stHeader"], section[data-testid="stSidebar"], .stButton { display: none !important; }
            @page { size: A4; margin: 10mm; }
        }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 6. [STEP 1] 문제 풀이 화면 (실전 모드 - CBT 툴바 및 동적 폰트 적용) 
# =====================================================================
elif not st.session_state.review_mode and not st.session_state.submitted:
    st.markdown(f"""
<div class="cbt-banner">
    <div class="title">01 {st.session_state.selected_exam_name}</div>
    <div class="info">
        {guest_expiry_banner}
        수험번호 : 0001
        수험자명 : {display_user_name}
        남은시간 : {remain_td}
</div>
""", unsafe_allow_html=True)

    col_main, col_omr = st.columns([7.5, 2.5], gap="large")
    
    with col_main:
        tb_col1, tb_col2 = st.columns(2)
        with tb_col1:
            st.session_state.font_exam = st.radio("🔍 글자크기", ["100%", "95%", "105%"], horizontal=True, key="font_exam_radio")
        with tb_col2:
            st.session_state.layout_exam = st.radio("📐 화면배치", ["세로(2단)", "가로(1단)"], horizontal=True, key="layout_exam_radio")
        st.markdown("---")

        QUESTIONS_PER_PAGE = 4 if st.session_state.layout_exam == "세로(2단)" else 5
        total_pages = math.ceil(len(questions) / QUESTIONS_PER_PAGE)
        
        if st.session_state.current_page > total_pages: 
            st.session_state.current_page = total_pages

        start_idx = (st.session_state.current_page - 1) * QUESTIONS_PER_PAGE
        end_idx = min(start_idx + QUESTIONS_PER_PAGE, len(questions))
        page_questions = questions[start_idx:end_idx]
        
        size_em = float(st.session_state.font_exam.replace("%", "")) / 100.0
        dynamic_img_width = int(current_img_width * size_em) 
        
        st.markdown(f"""
        <style>
            div[data-testid="stMarkdownContainer"] p {{
                font-size: {size_em}em !important;
                line-height: 1.6 !important;
                transition: font-size 0.2s ease-in-out;
            }}
            div[role="radiogroup"] label p, 
            div[role="radiogroup"] label div {{
                font-size: {size_em}em !important;
                line-height: 1.4 !important;
            }}
            button p {{ font-size: 16px !important; }}
            .cbt-banner p, .omr-header p, .bottom-bar-text p {{ font-size: inherit !important; }}
        </style>
        """, unsafe_allow_html=True)

        if st.session_state.layout_exam == "세로(2단)":
            q_cols = st.columns(2, gap="large")
            for i, item in enumerate(page_questions):
                actual_idx = start_idx + i 
                target_col = q_cols[0] if i < 2 else q_cols[1]
                
                with target_col:
                    wrong_badge = " <span style='color:#e74c3c; font-size:0.85em; font-weight:bold;'>[🚨 이전 오답]</span>" if item['q'] in st.session_state.wrong_history else ""
                    st.markdown(f"**{item['num']}. {item['q']}**{wrong_badge}", unsafe_allow_html=True)
                    
                    if item.get("image"):
                        try: st.image(item["image"], width=int(dynamic_img_width * 0.9))
                        except Exception: pass
                    
                    ans = st.session_state.user_answers.get(actual_idx)
                    ans_index = item['options'].index(ans) if ans in item['options'] else None
                    choice = st.radio("보기 선택", item['options'], key=f"q_{actual_idx}", index=ans_index, label_visibility="collapsed")
                    st.session_state.user_answers[actual_idx] = choice
                    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        else:
            for i, item in enumerate(page_questions):
                actual_idx = start_idx + i 
                wrong_badge = " <span style='color:#e74c3c; font-size:0.85em; font-weight:bold;'>[🚨 이전 오답]</span>" if item['q'] in st.session_state.wrong_history else ""
                st.markdown(f"**{item['num']}. {item['q']}**{wrong_badge}", unsafe_allow_html=True)
                
                if item.get("image"):
                    try: st.image(item["image"], width=dynamic_img_width)
                    except Exception: pass
                
                ans = st.session_state.user_answers.get(actual_idx)
                ans_index = item['options'].index(ans) if ans in item['options'] else None
                choice = st.radio("보기 선택", item['options'], key=f"q_{actual_idx}", index=ans_index, label_visibility="collapsed")
                st.session_state.user_answers[actual_idx] = choice
                st.markdown("---")
            
        st.markdown("<div class='bottom-bar'></div>", unsafe_allow_html=True)
        
        btn_calc, btn_prev, btn_page, btn_next, btn_submit = st.columns([1.5, 1.5, 2.5, 1.5, 2])
        
        with btn_calc: 
            st.button("🧮 계산기", disabled=True, use_container_width=True)
            
        with btn_prev:
            if st.session_state.current_page > 1:
                if st.button("◀ 이전", use_container_width=True):
                    st.session_state.current_page -= 1
                    st.rerun()
                    
        with btn_page: 
            st.markdown(f"<div class='bottom-bar-text' style='text-align: center; padding-top: 5px; font-size:15px;'><b>{st.session_state.current_page} / {total_pages} 페이지</b></div>", unsafe_allow_html=True)
            
        with btn_next:
            if st.session_state.current_page < total_pages:
                if st.button("다음 ▶", use_container_width=True):
                    st.session_state.current_page += 1
                    st.rerun()
                    
        with btn_submit:
            if st.button("✅ 답안 제출", type="primary", use_container_width=True):
                st.session_state.review_mode = True
                st.rerun()

    with col_omr:
        st.markdown("<div class='omr-header'>답안 표기란 (클릭 시 이동)</div>", unsafe_allow_html=True)
        with st.container(height=650):
            cols = st.columns(4)
            for idx in range(len(questions)):
                q_num = idx + 1
                is_answered = st.session_state.user_answers.get(idx) is not None
                btn_label = f"🟢 {q_num}" if is_answered else f"⚪ {q_num}"
                if cols[idx % 4].button(btn_label, key=f"omr_btn_{idx}", use_container_width=True):
                    st.session_state.current_page = (idx // QUESTIONS_PER_PAGE) + 1
                    st.rerun()


# =====================================================================
# 7. [STEP 2] 제출 전 OMR 검토 화면 
# =====================================================================
elif st.session_state.review_mode and not st.session_state.submitted:
    st.markdown(f"""
<div class="cbt-banner">
    <div class="title">01 {st.session_state.selected_exam_name}</div>
    <div class="info">
        {guest_expiry_banner}
        수험번호: 0001 | 수험자명: {display_user_name}
</div>
""", unsafe_allow_html=True)

    answered_count = sum(1 for val in st.session_state.user_answers.values() if val is not None)
    unanswered_count = len(questions) - answered_count

    if unanswered_count > 0:
        st.warning(f"⚠️ 아직 풀지 않은 문제가 **{unanswered_count}개** 있습니다. 노란색으로 표시된 문항을 확인하세요.")
    else:
        st.success("모든 문항의 답안 표기가 완료되었습니다.")

    cols_count = math.ceil(len(questions) / 20)
    grid_template = f"repeat({cols_count}, 1fr)"
    
    html_review = f"""
<div class="review-container">
<div class="review-info-panel">
<div class="review-info-header">수험자 정보</div>
<div class="review-info-body">
<b>시험명:</b><br>{st.session_state.selected_exam_name[:20]}<br><br>
<b>시험일자:</b> {today_str}<br><br>
<b>부:</b> 1<br><br>
{guest_expiry_review}<b>수험번호:</b> 0001<br>
<b>수험자명:</b> {display_user_name}<br>
<b>남은시간:</b> {remain_td}
</div>
<div class="review-omr-panel">
<div class="review-omr-header">답안표기란</div>
<div class="omr-review-grid" style="grid-template-columns: {grid_template};">
"""
    
    for col_idx in range(cols_count):
        html_review += '<div class="omr-col">'
        html_review += f'<div class="omr-subject-header">제 {col_idx + 1}과목</div>'
        
        start_q = col_idx * 20
        end_q = min(start_q + 20, len(questions))
        
        for idx in range(start_q, end_q):
            q_num = f"{idx + 1:02d}"
            ans = st.session_state.user_answers.get(idx)
            ans_idx = None
            if ans and ans in questions[idx]['options']:
                ans_idx = questions[idx]['options'].index(ans) + 1
            
            row_class = "omr-row unanswered" if ans_idx is None else "omr-row"
            
            dots = ""
            for opt_num in range(1, 5):
                if opt_num == ans_idx:
                    dots += '<span style="color:#000; font-size:16px;">⚫</span>'
                else:
                    circle_char = "①②③④"[opt_num - 1]
                    dots += f'<span style="color:#d9534f; font-size:15px; opacity:0.6;">{circle_char}</span>'
                    
            html_review += f'<div class="{row_class}"><span class="omr-num">{q_num}</span><div class="omr-dots">{dots}</div></div>'
            
        html_review += '</div>'

    html_review += """
</div>
<div style="padding: 10px 15px; color: #d9534f; font-size: 13px; font-weight:bold;">
* 문항번호를 클릭하면 해당 문항으로 이동합니다. (현재 구현은 이전 화면 복귀 기능 제공)
</div>
</div>
</div>
"""
    st.markdown(html_review, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([2, 6, 2])
    with col_btn1:
        if st.button("↩️ 답안 수정", use_container_width=True):
            st.session_state.review_mode = False
            st.rerun()
    with col_btn3:
        if st.button("2️⃣ 답안 최종 제출 ➡", type="primary", use_container_width=True):
            st.session_state.review_mode = False
            st.session_state.submitted = True
            st.session_state.end_time = time.time()
            st.rerun()


# =====================================================================
# 8. [STEP 3] 최종 결과 화면
# =====================================================================
elif st.session_state.submitted:
    correct_count = 0
    wrong_questions = []
    correct_questions = []

    for idx, item in enumerate(questions):
        my_answer = st.session_state.user_answers.get(idx)
        if my_answer == item['answer']:
            correct_count += 1
            correct_questions.append({"item": item, "my_answer": my_answer})
            if item['q'] in st.session_state.wrong_history:
                st.session_state.wrong_history.remove(item['q'])
        else:
            wrong_questions.append({"item": item, "my_answer": my_answer})
            st.session_state.wrong_history.add(item['q'])
            
    total_score = int((correct_count / len(questions)) * 100)
    
    is_pass = False
    is_fail_by_subject = False
    subject_scores = []
    
    if len(questions) in [80, 100]:
        num_subjects = len(questions) // 20
        for i in range(num_subjects):
            sub_correct = sum(1 for j in range(i*20, i*20+20) if st.session_state.user_answers.get(j) == questions[j]['answer'])
            sub_score = sub_correct * 5 
            subject_scores.append(sub_score)
            if sub_score < 40: is_fail_by_subject = True
        
        avg_score = sum(subject_scores) / num_subjects
        is_pass = (avg_score >= 60 and not is_fail_by_subject)
        final_score_display = f"{avg_score:.1f}"

    elif len(questions) == 60:
        for i in range(3):
            sub_correct = sum(1 for j in range(i*20, i*20+20) if st.session_state.user_answers.get(j) == questions[j]['answer'])
            subject_scores.append(sub_correct * 5)
        is_pass = (total_score >= 60)
        final_score_display = str(total_score)
    else:
        is_pass = (total_score >= 60)
        final_score_display = str(total_score)

    banner_class = "result-pass" if is_pass else "result-fail"
    banner_msg = "합격을 축하드립니다." if is_pass else "불합격입니다. 부족한 부분을 보완하여 다시 도전하세요."
    status_text = "합격" if is_pass else "불합격"
    status_class = "result-score-pass" if is_pass else "result-score-fail"

    st.markdown(f"""
<div class="result-banner {banner_class}">
    {banner_msg}
</div>
<table class="result-table">
    <tr>
        <th>수험자 이름</th>
        <td>{display_user_name}</td>
    </tr>
    <tr>
        <th>응시종목</th>
        <td>{st.session_state.selected_exam_name[:20]}</td>
    </tr>
    <tr>
        <th>득점</th>
        <td class="{status_class}">{final_score_display} 점</td>
    </tr>
    <tr>
        <th>가채점결과</th>
        <td class="{status_class}">{status_text}</td>
    </tr>
</table>
""", unsafe_allow_html=True)
    
    if subject_scores:
        sub_html = "<table class='result-table'><tr><th>세부과목명</th><th>득점</th><th>비고(과락)</th></tr>"
        for i, score in enumerate(subject_scores):
            note = "<span style='color:red;font-weight:bold;'>과락</span>" if score < 40 and len(questions) != 60 else "-"
            sub_html += f"<tr><td>제 {i+1}과목</td><td>{score}</td><td>{note}</td></tr>"
        sub_html += "</table>"
        st.markdown(sub_html, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("1️⃣ 확인 완료 (메인으로 돌아가기)", type="primary", use_container_width=True):
            st.session_state.user_answers = {}
            st.session_state.review_mode = False
            st.session_state.submitted = False
            st.session_state.study_mode = False
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
                with st.expander(f"Q{item['num']} 오답 분석 (정답: {item['answer']})"):
                    st.write(f"**문제:** {item['q']}")
                    if item.get("image"):
                        try: st.image(item["image"], width=tab_img_width)
                        except Exception: pass
                    st.error(f"내 선택: {my_ans if my_ans else '미선택'}")
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

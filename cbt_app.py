# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import math
import re

# 화면을 넓게 쓰는 실전형 와이드 레이아웃
st.set_page_config(page_title="국가기술자격 실전 CBT", page_icon="⚡", layout="wide")

st.title("⚡ 실전 CBT")

# 1. 기출문제 동적 매핑
exam_mapping = {
    "26년도 소방설비기사(전기) 2회차 시험 (202602)": "2602", 
    "26년도 소방설비기사(전기) 1회차 시험 (202601)": "2601", 
    "25년도 다산 소방설비기사(전기) 3회차 시험 (202503)": "D2503", 
    "25년도 다산 소방설비기사(전기) 2회차 시험 (202502)": "D2502",     
    "25년도 다산 소방설비기사(전기) 1회차 시험 (202501)": "D2501", 
    "24년도 다산 소방설비기사(전기) 3회차 시험 (202403)": "D2403",
    "24년도 다산 소방설비기사(전기) 2회차 시험 (202402)": "D2402",
    "24년도 다산 소방설비기사(전기) 1회차 시험 (202401)": "D2401",   
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
if 'wrong_counts' not in st.session_state:
    st.session_state.wrong_counts = {}
    
# (자동으로 UI와 연동되는 이미지 확대 세션 변수 초기화)
if 'img_expanded' not in st.session_state:
    st.session_state.img_expanded = False

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


# ---------------------------------------------------------
# 💡 [화면용] 토글 상태에 따른 이미지 폭 전역 결정
# ---------------------------------------------------------
current_img_width = 450 if st.session_state.img_expanded else 250
tab_img_width = 400 if st.session_state.img_expanded else 200


# 4. 우측 고정형 실시간 OMR 사이드바 및 흐름 제어 스위치
with st.sidebar:
    st.header("📋 OMR 답안지")
    
    if not st.session_state.submitted:
        st.info("문제를 풀면 답안이 실시간으로 기록됩니다.")
        answered_count = len([ans for ans in st.session_state.user_answers.values() if ans is not None])
        st.progress(answered_count / len(questions), text=f"풀이 진행률: {answered_count} / {len(questions)}")
        
        if st.button("✅ 최종 답안 제출 및 채점", type="primary", use_container_width=True):
            st.session_state.submitted = True
            st.rerun()
    else:
        st.success("채점이 완료되었습니다.")
        if st.button("🔄 다른 시험 보기 (초기화)", use_container_width=True):
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.current_page = 1
            st.rerun()

    st.markdown("---")
    
    # 💡 그림 크게 보기 스위치
    st.toggle("🔍 그림 크게 보기", key="img_expanded", help="문제에 포함된 도면이나 그림을 확대합니다.")
    
    print_mode = st.toggle("🖨️ 전체 문제 인쇄 모드", help="전체 문항을 실제 시험지 양식으로 출력합니다.")
    
    # 인쇄 모드가 켜졌을 때 다각적 관점으로 선택 가능한 출력 옵션
    print_option = "문제만 인쇄"
    if print_mode:
        print_option = st.radio(
            "📝 출력 옵션 선택",
            ["문제만 인쇄", "정답만 표기", "정답 및 해설 표기"],
            horizontal=True
        )

# ---------------------------------------------------------
# 5. 실제 시험지 스타일 및 레이아웃 강제 통제 (인쇄 모드)
# ---------------------------------------------------------
if print_mode:
    st.markdown("## 🖨️ 인쇄용 전체 문제 보기 (시험지 모드)")
    st.info("💡 **출력 팁:** 인쇄 창(Ctrl+P)이 열리면 설정에서 **'머리글 및 바닥글'을 체크 해제**하세요.")
    
    exam_paper_css = """
    <style>
    .exam-options {
        display: flex;
        flex-direction: column;
        gap: 5px;
        font-size: 0.95em;
        margin-top: 10px;
        margin-bottom: 12px;
    }
    
    .print-answer-only {
        margin-top: 10px;
        margin-bottom: 25px !important;
        font-size: 0.95em;
        font-weight: bold;
    }

    .print-answer-box {
        display: block;
        margin-top: 15px;
        margin-bottom: 35px !important; 
        padding-top: 12px;
        border-top: 1.5px dashed #666;
        font-size: 0.92em;
        line-height: 1.5;
        clear: both;
    }
    
    @media print {
        @page { size: A4; margin: 12mm; }
        
        header[data-testid="stHeader"], 
        section[data-testid="stSidebar"], 
        .stButton, div[data-testid="stCaptionContainer"] { display: none !important; }
        
        div.block-container * {
            color: #000000 !important;
            opacity: 1 !important;
            text-shadow: none !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        div.block-container { 
            padding: 0 !important; 
            max-width: 100% !important; 
            column-count: 2 !important;
            column-gap: 30px !important;
            column-rule: 1px solid #000 !important;
        }

        p, div, span { font-size: 10.5pt !important; line-height: 1.4 !important; }
        strong { font-size: 11pt !important; }

        /* 💡 수정된 핵심 영역: 인쇄 시 이미지 폭주 및 침범 완벽 차단 */
        div[data-testid="stImage"], 
        div[data-testid="stImage"] > div,
        div[data-testid="stImage"] img {
            max-width: 100% !important; /* 물리적 단(Column) 너비를 절대 넘지 못하도록 강제 */
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
            margin-bottom: 10px !important;
        }
        
        div.block-container > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            display: inline-block !important; 
            width: 100% !important;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            -webkit-column-break-inside: avoid !important;
            margin-bottom: 5px !important;
            padding-bottom: 20px !important;
            vertical-align: top !important;
            box-sizing: border-box !important;
            transform: translateZ(0) !important; 
        }
    }
    </style>
    """
    st.markdown(exam_paper_css, unsafe_allow_html=True)
    
    if st.button("🖨️ 인쇄 창 열기", type="primary"):
        st.components.v1.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")
    
    # 💡 [핵심] 인쇄 전용 안전 이미지 폭 설정 (화면 토글과 관계없이 A4 2단에 최적화된 크기로 고정)
    PRINT_IMG_WIDTH = 250 

    symbols = ['①', '②', '③', '④', '⑤']
    
    for item in questions:
        with st.container():
            st.markdown(f"**{item['num']}. {item['q']}**")
            
            # 인쇄 모드에서는 무조건 PRINT_IMG_WIDTH(250) 적용
            if item.get("image"):
                try: 
                    st.image(item["image"], width=PRINT_IMG_WIDTH)
                except Exception: 
                    pass
            
            combined_html = "<div class='exam-options'>"
            for idx, opt in enumerate(item['options']):
                clean_opt = re.sub(r'^[\s①②③④⑤]+|^(?:[1-5]\.|\([1-5]\))\s*', '', str(opt))
                sym = symbols[idx] if idx < len(symbols) else f"({idx+1})"
                combined_html += f"<div>{sym} {clean_opt}</div>"
            combined_html += "</div>"
            
            if print_option == "정답만 표기":
                ans_text = item.get("answer", "정보 없음")
                combined_html += f"<div class='print-answer-only'>✅ 정답: {ans_text}<br><br></div>"
            elif print_option == "정답 및 해설 표기":
                ans_text = item.get("answer", "정보 없음")
                exp_text = item.get("explanation", "해설 없음")
                combined_html += f"<div class='print-answer-box'><strong>✅ 정답:</strong> {ans_text}<br><br><strong>💡 해설:</strong> {exp_text}<br><br><br></div>"
            
            st.markdown(combined_html, unsafe_allow_html=True)
    
    st.stop() 


# 6. 본문 문제 풀이 영역 (제출 전)
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
            q_key = f"{selected_module_name}_{item['num']}"
            wrong_count = st.session_state.wrong_counts.get(q_key, 0)
            if wrong_count > 0:
                st.markdown(f"<span style='color: #FF4B4B; font-size: 0.85rem; font-weight: bold;'>🚨 {wrong_count}회 틀림</span>", unsafe_allow_html=True)
                
            st.markdown(f"**{item['num']}. {item['q']}**")
            
            # 본문 풀이 영역에서는 사용자가 선택한 current_img_width (250 또는 450) 정상 적용
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
                key=f"q_{selected_module_name}_{actual_idx}", 
                index=ans_index,
                label_visibility="collapsed" 
            )
            st.session_state.user_answers[actual_idx] = choice
            st.markdown("---")

    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    
    with btn_col1:
        if st.session_state.current_page > 1:
            if st.button("◀ 이전 페이지", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
                
    with btn_col2:
        st.markdown(f"<h4 style='text-align: center; color: gray;'>Page {st.session_state.current_page} / {total_pages}</h4>", unsafe_allow_html=True)
        
    with btn_col3:
        if st.session_state.current_page < total_pages:
            if st.button("다음 페이지 ▶", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

# 7. 채점 및 결과 대시보드 (제출 후)
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
                    if item.get("image"):
                        try: st.image(item["image"], width=tab_img_width)
                        except Exception: pass
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
                    if item.get("image"):
                        try: st.image(item["image"], width=tab_img_width)
                        except Exception: pass
                    st.success(f"내 선택 & 정답: {my_ans}")
                    st.info(f"💡 해설: {item['explanation']}")

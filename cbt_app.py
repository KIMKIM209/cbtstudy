import streamlit as st
from questions import questions # 우리가 자동 변환한 문제 데이터

# 페이지 기본 설정
st.set_page_config(page_title="전기기능사 실전 모의고사", page_icon="⚡", layout="centered")

st.title("⚡ 전기기능사 실전 CBT")

# 메모리 탱크(세션 상태) 초기화
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.write(f"총 {len(questions)}문제 중 나의 현재 위치를 점검합니다.")

# 1. 문제 풀이 화면
for idx, item in enumerate(questions):
    st.markdown("---")
    st.subheader(f"Q{item['num']}. {item['q']}")
    
    # 보기 출력 (제출 후에는 비활성화되어 수정 불가)
    choice = st.radio(
        "보기 선택:", 
        item['options'], 
        key=f"q_{idx}", 
        index=None,
        disabled=st.session_state.submitted 
    )
    # 사용자의 선택을 메모리에 실시간 저장
    st.session_state.user_answers[idx] = choice

st.markdown("---")

# 2. 채점 및 결과 화면 로직
if not st.session_state.submitted:
    # 제출 전 화면
    if st.button("🏁 시험 종료 및 채점하기", type="primary"):
        st.session_state.submitted = True
        st.rerun()
else:
    # 제출 후 채점 진행
    correct_count = 0
    wrong_questions = []

    for idx, item in enumerate(questions):
        # 내가 고른 답과 실제 정답 비교
        my_answer = st.session_state.user_answers.get(idx)
        if my_answer == item['answer']:
            correct_count += 1
        else:
            # 틀린 문제는 별도의 리스트로 수집
            wrong_questions.append({
                "item": item,
                "my_answer": my_answer
            })

    # 백분율 점수 계산
    score = int((correct_count / len(questions)) * 100)
    
    # 상단 대시보드 출력
    st.header("📊 최종 채점 결과")
    col1, col2, col3 = st.columns(3)
    col1.metric("내 점수", f"{score}점")
    col2.metric("맞은 문제", f"{correct_count}개")
    col3.metric("틀린 문제", f"{len(wrong_questions)}개")

    if score >= 60:
        st.success("🎉 합격권입니다! 이 감각을 유지하십시오.")
    else:
        st.warning("⚠️ 보완이 필요합니다. 아래 오답 노트에 에너지를 집중하십시오.")

    # 3. 자동 오답 노트 생성
    if wrong_questions:
        st.subheader("📝 나의 자동 오답 노트")
        for wrong in wrong_questions:
            item = wrong["item"]
            my_ans = wrong["my_answer"]
            
            with st.expander(f"Q{item['num']} 오답 확인"):
                st.write(f"**문제:** {item['q']}")
                st.error(f"내 선택: {my_ans if my_ans else '미선택'}")
                st.success(f"정답: {item['answer']}")
                st.info(f"💡 해설: {item['explanation']}")
    
    # 다시 풀기 버튼 (메모리 탱크 초기화)
    st.markdown("---")
    if st.button("🔄 새로운 마음으로 다시 풀기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

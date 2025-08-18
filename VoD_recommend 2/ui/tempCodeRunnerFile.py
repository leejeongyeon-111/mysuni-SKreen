    info_cols = st.columns(6)
    actors = ", ".join(str(row.get('배우', '')).split(',')[:3])
    # <div>로 감싸고 font_style을 적용합니다.
    info_cols[0].markdown(f"<div style='{font_style}'><b>배우</b><br>{actors}</div>", unsafe_allow_html=True)
    info_cols[1].markdown(f"<div style='{font_style}'><b>감독</b><br>{row.get('감독', '-')}</div>", unsafe_allow_html=True)
    maker = str(row.get('제작사', '')).split(',')[0]
    info_cols[2].markdown(f"<div style='{font_style}'><b>제작사</b><br>{maker}</div>", unsafe_allow_html=True)
    info_cols[3].markdown(f"<div style='{font_style}'><b>누적관객</b><br>{format_number_display(row.get('누적 관객수'))}명</div>", unsafe_allow_html=True)
    info_cols[4].markdown(f"<div style='{font_style}'><b>시청자 수</b><br>{format_number_display(row.get('매력도'))}</div>", unsafe_allow_html=True)
    # 그라데이션 스타일은 그대로 유지합니다. 폰트 크기는 부모 div로부터 상속받습니다.
    gradient_style = "background-image: linear-gradient(to right, #FF8C00, #9400D3);-webkit-background-clip: text;background-clip: text;color: transparent;font-weight: bold;"
    info_cols[5].markdown(f"<div style='{font_style}'><b>AI 키워드</b><br><span style='{gradient_style}'>{row.get('Gemini 키워드', '-')}</span></div>", unsafe_allow_html=True)
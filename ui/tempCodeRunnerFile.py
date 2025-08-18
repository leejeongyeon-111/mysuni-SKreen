    info_cols = st.columns(6)
    actors = ", ".join(str(row.get('배우', '')).split(',')[:3])
   
    info_cols[0].markdown(f"<div style='{font_style}'><b>배우</b><br>{actors}</div>", unsafe_allow_html=True)
    info_cols[1].markdown(f"<div style='{font_style}'><b>감독</b><br>{row.get('감독', '-')}</div>", unsafe_allow_html=True)
    maker = str(row.get('제작사', '')).split(',')[0]
    info_cols[2].markdown(f"<div style='{font_style}'><b>제작사</b><br>{maker}</div>", unsafe_allow_html=True)
    info_cols[3].markdown(f"<div style='{font_style}'><b>누적관객</b><br>{format_number_display(row.get('누적 관객수'))}명</div>", unsafe_allow_html=True)
    info_cols[4].markdown(f"<div style='{font_style}'><b>시청자 수</b><br>{format_number_display(row.get('매력도'))}</div>", unsafe_allow_html=True)

    gradient_style = "background-image: linear-gradient(to right, #FF8C00, #9400D3);-webkit-background-clip: text;background-clip: text;color: transparent;font-weight: bold;"

    info_cols[5].markdown(f"<div style='{font_style}'><b>AI 키워드</b><br><span style='{gradient_style}'>{row.get('Gemini 키워드', '-')}</span></div>", unsafe_allow_html=True)

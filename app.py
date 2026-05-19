import streamlit as st
import json
import os

# 1. 数据持久化配置（会把小说保存在同文件夹下的 json 文件里）
DATA_FILE = 'chapters_data.json'

def load_chapters():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_chapters(chapters):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=4)

# 2. 状态初始化
if 'chapters' not in st.session_state:
    st.session_state.chapters = load_chapters()
if 'reading_chapter' not in st.session_state:
    st.session_state.reading_chapter = None

# 3. 页面渲染逻辑
st.set_page_config(page_title="我的小说后台", page_icon="📖", layout="centered")

# --- 阅读模式视图 ---
if st.session_state.reading_chapter:
    chapter = st.session_state.reading_chapter
    
    if st.button("⬅️ 返回后台列表"):
        st.session_state.reading_chapter = None
        st.rerun()
        
    st.title(chapter['title'])
    # 保留换行符，适合小说排版
    st.markdown(chapter['content'].replace('\n', '\n\n'))

# --- 后台管理视图 ---
else:
    st.title("📖 我的小说后台")
    
    st.markdown("---")
    st.subheader("➕ 添加新章节")
    
    # 填写表单
    with st.form("add_chapter_form", clear_on_submit=True):
        new_title = st.text_input("章节标题")
        new_content = st.text_area("章节内容", height=150)
        submitted = st.form_submit_button("发布章节")
        
        if submitted:
            if not new_title.strip() or not new_content.strip():
                st.error("标题和内容不能为空！")
            else:
                new_chapter = {"title": new_title, "content": new_content}
                st.session_state.chapters.append(new_chapter)
                save_chapters(st.session_state.chapters)
                st.success("章节发布成功！")
                st.rerun()

    st.markdown("---")
    st.subheader("📚 已发布章节列表")
    
    if not st.session_state.chapters:
        st.info("暂无数据，快去发布第一章吧！")
    else:
        for idx, chapter in enumerate(st.session_state.chapters):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{chapter['title']}**")
                    st.caption(f"{chapter['content'][:50]}...")
                    if st.button("阅读正文", key=f"read_{idx}"):
                        st.session_state.reading_chapter = chapter
                        st.rerun()
                        
                with col2:
                    if st.button("删除", key=f"del_{idx}"):
                        st.session_state.chapters.pop(idx)
                        save_chapters(st.session_state.chapters)
                        st.rerun()
            st.divider()
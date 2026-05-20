import streamlit as st
from supabase import create_client, Client

# 1. 连接你的专属云端数据库
# 注意：我已经帮你把 URL 修剪成了标准的连接格式
URL = "https://ajjropcbivsvyjzwrgyw.supabase.co"
KEY = "sb_publishable_oHEWVybqEgyGaJZFJoxT1w_ViLc9mWV"
supabase: Client = create_client(URL, KEY)

# 2. 状态初始化
if 'reading_chapter' not in st.session_state:
    st.session_state.reading_chapter = None

# 3. 核心功能：从云端拉取数据
def fetch_chapters():
    # 按照创建时间排序拉取所有章节
    response = supabase.table("chapters").select("*").order("created_at", desc=False).execute()
    return response.data

# 每次刷新页面都会实时从云端获取最新列表
chapters = fetch_chapters()

# --- 页面渲染逻辑 ---
st.set_page_config(page_title="我的云端小说后台", page_icon="☁️", layout="centered")

# 【阅读模式】
if st.session_state.reading_chapter:
    chapter = st.session_state.reading_chapter
    
    if st.button("⬅️ 返回后台列表"):
        st.session_state.reading_chapter = None
        st.rerun()
        
    st.title(chapter['title'])
    st.markdown(chapter['content'].replace('\n', '\n\n'))

# 【后台管理模式】
else:
    st.title("☁️ 我的云端小说后台")
    
    st.markdown("---")
    st.subheader("➕ 添加新章节 (自动同步至云端)")
    
    with st.form("add_chapter_form", clear_on_submit=True):
        new_title = st.text_input("章节标题")
        new_content = st.text_area("章节内容", height=150)
        submitted = st.form_submit_button("发布章节")
        
        if submitted:
            if not new_title.strip() or not new_content.strip():
                st.error("标题和内容不能为空！")
            else:
                # 【魔法发生的地方】：直接把标题和内容写入 Supabase 云端
                supabase.table("chapters").insert({"title": new_title, "content": new_content}).execute()
                st.success("章节发布成功！已永久保存至云端。")
                st.rerun()

    st.markdown("---")
    st.subheader("📚 云端章节列表")
    
    if not chapters:
        st.info("云端暂无数据，快去发布第一章吧！")
    else:
        for chapter in chapters:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{chapter['title']}**")
                    st.caption(f"{chapter['content'][:50]}...")
                    # 注意：这里的 id 是 Supabase 自动生成的唯一编号
                    if st.button("阅读正文", key=f"read_{chapter['id']}"):
                        st.session_state.reading_chapter = chapter
                        st.rerun()
                        
                with col2:
                    if st.button("删除", key=f"del_{chapter['id']}"):
                        # 从云端精准删除这一章
                        supabase.table("chapters").delete().eq("id", chapter["id"]).execute()
                        st.rerun()
            st.divider()
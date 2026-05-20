import streamlit as st
from supabase import create_client, Client
import os
import time

# --- 1. 页面配置 ---
st.set_page_config(page_title="锦汐的个人主页", page_icon="✨", layout="wide")

# --- 2. 连接云端数据库 ---
@st.cache_resource
def init_connection():
    URL = "https://ajjropcbivsvyjzwrgyw.supabase.co"
    KEY = "sb_publishable_oHEWVybqEgyGaJZFJoxT1w_ViLc9mWV"
    return create_client(URL, KEY)

supabase = init_connection()

# --- 3. 站长身份验证 ---
with st.sidebar:
    st.title("🔐 站长通道")
    admin_password = st.text_input("暗号", type="password")
    is_admin = (admin_password == "8888") 
    if is_admin:
        st.success("欢迎回来，主人！")

# --- 4. 提速缓存 ---
@st.cache_data(ttl=10)
def fetch_data(table_name):
    response = supabase.table(table_name).select("*").order("created_at", desc=False).execute()
    return response.data

chapters = fetch_data("chapters")
thoughts = fetch_data("thoughts")
photo_records = fetch_data("photos")

# --- 状态初始化 ---
if 'reading_chapter' not in st.session_state:
    st.session_state.reading_chapter = None

# --- 阅读模式 ---
if st.session_state.reading_chapter:
    chapter = st.session_state.reading_chapter
    if st.button("⬅️ 返回主页"):
        st.session_state.reading_chapter = None
        st.rerun()
    st.title(chapter['title'])
    st.markdown(chapter['content'].replace('\n', '\n\n'))

# --- 主界面 ---
else:
    col1, col2, col3 = st.columns([1.5, 1.5, 1], gap="large")

    # ================= 列 1：小说连载 =================
    with col1:
        st.header("📖 小说后台")
        if is_admin:
            with st.expander("➕ 发布新章节"):
                new_title = st.text_input("章节标题")
                new_content = st.text_area("章节内容", height=150)
                if st.button("立即发布"):
                    supabase.table("chapters").insert({"title": new_title, "content": new_content}).execute()
                    fetch_data.clear()
                    st.rerun()

        for chapter in chapters:
            with st.container(border=True):
                st.markdown(f"**{chapter['title']}**")
                if st.button("阅读正文", key=f"read_{chapter['id']}"):
                    st.session_state.reading_chapter = chapter
                    st.rerun()
                if is_admin:
                    if st.button("🗑️ 删除", key=f"del_{chapter['id']}"):
                        supabase.table("chapters").delete().eq("id", chapter["id"]).execute()
                        fetch_data.clear()
                        st.rerun()
# ============== 👇 新加的代码：社交链接 ==============
        st.markdown("---")
        st.subheader("🔗 关注我")
        # 把下面括号里的 # 换成你真实的个人主页链接！
        st.markdown("🍓 [小红书](https://xhslink.com/m/6Zh7aaViNPL)")
        st.markdown("💼 [抖音](https://v.douyin.com/b5-iprgkuJE/)")
        st.markdown("🏫 [简历](#)")
        st.markdown("🏫 [追星号，进来看幂姐](#)")
        # ============== 👆 新加的代码结束 ==============
    # ================= 列 2：胡思乱想 & 我是大师 =================
    with col2:
        st.header("💭 胡思乱想")
        if is_admin:
            with st.form("thought_form", clear_on_submit=True):
                new_thought = st.text_area("碎碎念...", height=60)
                if st.form_submit_button("发布"):
                    supabase.table("thoughts").insert({"content": new_thought}).execute()
                    fetch_data.clear()
                    st.rerun()
        
        for thought in reversed(thoughts):
            st.info(thought['content'])
            if is_admin:
                if st.button("删除", key=f"del_t_{thought['id']}"):
                    supabase.table("thoughts").delete().eq("id", thought["id"]).execute()
                    fetch_data.clear()
                    st.rerun()

        st.markdown("---")
        st.header("📷 我是大师")
        
        # --- 图片上传逻辑 ---
        if is_admin:
            uploaded_file = st.file_uploader("上传摄影作品", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                if st.button("确认上传照片"):
                    with st.spinner("正在上传至云端..."):
                        # 1. 上传到 Storage
                        file_name = f"{int(time.time())}_{uploaded_file.name}"
                        file_data = uploaded_file.getvalue()
                        supabase.storage.from_("photos").upload(file_name, file_data)
                        
                        # 2. 获取公开链接
                        img_url = supabase.storage.from_("photos").get_public_url(file_name)
                        
                        # 3. 存入数据库表
                        supabase.table("photos").insert({"url": img_url}).execute()
                        fetch_data.clear()
                        st.success("照片已入库！")
                        st.rerun()
        
        # --- 展示照片墙 ---
        if not photo_records:
            st.caption("大师还没上传照片哦~")
        else:
            for photo in reversed(photo_records):
                st.image(photo['url'], use_container_width=True)
                if is_admin:
                    if st.button("删除这张照片", key=f"del_p_{photo['id']}"):
                        # 从数据库删除记录
                        supabase.table("photos").delete().eq("id", photo["id"]).execute()
                        fetch_data.clear()
                        st.rerun()

    # ================= 列 3：明星日程 & 收款码 =================
    with col3:
        st.header("📅 明星日程")
        st.text_input("5月", value="准备毕业论文答辩", disabled=True)
        st.text_input("5月07日-6月30日", value="前往银行参加实习", disabled=True)
        st.text_input("2026-2027", value="申请博士投递材料", disabled=True)
        
        st.write("")
        if st.button("💎 充值VIP获取独家行程", type="primary", use_container_width=True):
            if os.path.exists("qr.png"): st.image("qr.png", caption="扫码充值，感谢老板！")
            elif os.path.exists("qr.jpg"): st.image("qr.jpg", caption="扫码充值，感谢老板！")
            else: st.error("请在文件夹中放入名为 qr.png 的收款码图片！")
st.markdown("---")
       
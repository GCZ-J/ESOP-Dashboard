import streamlit as st
from datetime import datetime

st.set_page_config(page_title="股权激励管理", layout="wide")
st.title("🏢 股权激励年度股票池管理")

# 模拟数据
level_standards = {'P6': 20000, 'P7': 40000, 'P8': 80000}
employees = [
    {'工号': 'E001', '姓名': '张三', '部门': '研发部', '职级': 'P7', '状态': '在职'},
    {'工号': 'E002', '姓名': '李四', '部门': '产品部', '职级': 'P6', '状态': '在职'},
    {'工号': 'E003', '姓名': '王五', '部门': '市场部', '职级': 'P8', '状态': '在职'},
]

stock_pool = 5000000

# 计算
total_shares = 0
for emp in employees:
    if emp['状态'] == '在职':
        total_shares += level_standards.get(emp['职级'], 0)

# 显示
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("股票池总额", f"{stock_pool:,}股")
with col2:
    st.metric("已使用", f"{total_shares:,}股")
with col3:
    usage = (total_shares / stock_pool * 100) if stock_pool > 0 else 0
    st.metric("使用率", f"{usage:.1f}%")

st.progress(min(usage/100, 1.0))

# 员工列表
st.subheader("员工列表")
for emp in employees:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write(f"**{emp['姓名']}** ({emp['工号']})")
    with col2:
        st.write(emp['部门'])
    with col3:
        st.write(emp['职级'])
    with col4:
        st.write(f"{level_standards.get(emp['职级'], 0):,}股")

st.success("✅ 演示版运行成功！")

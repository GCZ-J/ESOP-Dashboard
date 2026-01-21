import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 设置页面
st.set_page_config(page_title="股权激励管理Demo", layout="wide")

st.title("🏢 股权激励年度股票池管理Demo")
st.markdown("---")

# 初始化数据
if 'level_standards' not in st.session_state:
    st.session_state.level_standards = {
        'P5': 10000, 'P6': 20000, 'P7': 40000, 'P8': 80000,
        'M1': 50000, 'M2': 100000, 'M3': 200000
    }
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'stock_pool_total' not in st.session_state:
    st.session_state.stock_pool_total = 5000000
if 'stock_pool_used' not in st.session_state:
    st.session_state.stock_pool_used = 0

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 股票池设置
    pool_total = st.number_input("年度股票池总额（万股）", 100, 10000, 500, 50)
    if st.button("设置股票池"):
        st.session_state.stock_pool_total = pool_total * 10000
        st.success(f"股票池已设置为 {pool_total:,} 万股")
    
    st.info(f"""
    **股票池状态:**
    - 总额: {st.session_state.stock_pool_total:,} 股
    - 已使用: {st.session_state.stock_pool_used:,} 股
    - 剩余: {st.session_state.stock_pool_total - st.session_state.stock_pool_used:,} 股
    """)
    
    st.markdown("---")
    if st.button("生成示例数据"):
        # 生成示例员工
        departments = ['研发部', '产品部', '市场部', '销售部']
        for i in range(1, 21):
            st.session_state.employees.append({
                'employee_id': f'E{i:04d}',
                'name': f'员工{i}',
                'department': np.random.choice(departments),
                'level': np.random.choice(['P6', 'P7', 'P8']),
                'join_date': '2024-01-01',
                'status': '在职'
            })
        st.success("示例数据生成完成！")
        st.rerun()

# 主界面
tab1, tab2, tab3 = st.tabs(["📊 仪表盘", "🎯 职级标准", "👥 员工管理"])

with tab1:
    st.header("📊 股权激励预算池仪表盘")
    
    # 计算总需求
    total_shares = 0
    for emp in st.session_state.employees:
        if emp.get('status') == '在职':
            level = emp.get('level', '')
            shares = st.session_state.level_standards.get(level, 0)
            total_shares += shares
    
    st.session_state.stock_pool_used = total_shares
    remaining = st.session_state.stock_pool_total - total_shares
    
    # 关键指标
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("在职员工数", len(st.session_state.employees))
    with col2:
        st.metric("年度总需求", f"{total_shares:,} 股")
    with col3:
        usage_rate = (total_shares / st.session_state.stock_pool_total * 100) if st.session_state.stock_pool_total > 0 else 0
        st.metric("使用率", f"{usage_rate:.1f}%")
    
    # 股票池进度条
    st.progress(min(usage_rate/100, 1.0))
    
    # 预警
    if usage_rate > 80:
        st.warning(f"⚠️ 股票池使用率较高 ({usage_rate:.1f}%)")
    elif usage_rate > 90:
        st.error(f"🚨 股票池使用率过高 ({usage_rate:.1f}%)")
    else:
        st.success(f"✅ 股票池使用正常 ({usage_rate:.1f}%)")

with tab2:
    st.header("🎯 职级标准设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("当前职级标准")
        levels_df = pd.DataFrame([
            {'职级': level, '年度股数': shares}
            for level, shares in st.session_state.level_standards.items()
        ])
        st.dataframe(levels_df)
    
    with col2:
        st.subheader("添加/修改标准")
        with st.form("level_form"):
            level = st.text_input("职级（如: P7）")
            shares = st.number_input("年度股数", 0, 1000000, 20000, 1000)
            if st.form_submit_button("保存"):
                if level:
                    st.session_state.level_standards[level] = shares
                    st.success(f"已设置 {level} 为 {shares:,} 股/年")
                    st.rerun()

with tab3:
    st.header("👥 员工管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        if st.session_state.employees:
            employees_df = pd.DataFrame(st.session_state.employees)
            st.dataframe(employees_df)
        else:
            st.info("暂无员工数据")
    
    with col2:
        st.subheader("添加员工")
        with st.form("add_employee_form"):
            name = st.text_input("姓名")
            department = st.selectbox("部门", ["研发部", "产品部", "市场部", "销售部"])
            level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
            
            if st.form_submit_button("添加员工"):
                if name:
                    new_id = f'E{len(st.session_state.employees) + 1:04d}'
                    st.session_state.employees.append({
                        'employee_id': new_id,
                        'name': name,
                        'department': department,
                        'level': level,
                        'join_date': datetime.now().strftime('%Y-%m-%d'),
                        'status': '在职'
                    })
                    st.success(f"已添加员工: {name}")
                    st.rerun()
        
        st.subheader("操作")
        if st.session_state.employees and st.button("模拟员工离职（随机1人）"):
            if st.session_state.employees:
                idx = np.random.randint(0, len(st.session_state.employees))
                emp = st.session_state.employees.pop(idx)
                st.warning(f"已模拟离职: {emp['name']}")
                st.rerun()

st.markdown("---")
st.caption("🏢 股权激励管理Demo | 最小化版本，用于快速演示")

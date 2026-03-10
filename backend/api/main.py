"""
FastAPI 后端服务
提供日报查询、标的管理等 API
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import init_db, get_session, DailyReport, Symbol, DailyQuote
from backend.reports.report_generator import ReportGenerator

app = FastAPI(title="Finance Dash API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 报告相关 ============

@app.get("/api/reports")
def list_reports(
    report_type: Optional[str] = Query(None, description="报告类型：noon/daily"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100)
):
    """获取报告列表"""
    session = get_session()
    try:
        query = session.query(DailyReport)
        
        if report_type:
            query = query.filter(DailyReport.report_type == report_type)
        if start_date:
            query = query.filter(DailyReport.report_date >= start_date)
        if end_date:
            query = query.filter(DailyReport.report_date <= end_date)
        
        reports = query.order_by(DailyReport.report_date.desc()).limit(limit).all()
        
        return {
            "count": len(reports),
            "data": [
                {
                    "id": r.id,
                    "report_date": r.report_date,
                    "report_type": r.report_type,
                    "summary": r.summary,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reports
            ]
        }
    finally:
        session.close()


@app.get("/api/reports/{report_id}")
def get_report(report_id: int):
    """获取报告详情"""
    session = get_session()
    try:
        report = session.query(DailyReport).filter(DailyReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        return {
            "id": report.id,
            "report_date": report.report_date,
            "report_type": report.report_type,
            "content": report.content,
            "summary": report.summary,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    finally:
        session.close()


@app.get("/api/reports/latest")
def get_latest_report(report_type: Optional[str] = None):
    """获取最新报告"""
    session = get_session()
    try:
        query = session.query(DailyReport)
        if report_type:
            query = query.filter(DailyReport.report_type == report_type)
        
        report = query.order_by(DailyReport.report_date.desc()).first()
        if not report:
            raise HTTPException(status_code=404, detail="暂无报告")
        
        return {
            "id": report.id,
            "report_date": report.report_date,
            "report_type": report.report_type,
            "content": report.content,
            "summary": report.summary,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    finally:
        session.close()


# ============ 标的管理 ============

class SymbolCreate(BaseModel):
    symbol: str
    name: str
    market: str
    category: Optional[str] = 'stock'


@app.get("/api/symbols")
def list_symbols(is_active: Optional[int] = None):
    """获取监控标的列表"""
    session = get_session()
    try:
        query = session.query(Symbol)
        if is_active is not None:
            query = query.filter(Symbol.is_active == is_active)
        
        symbols = query.all()
        return {
            "count": len(symbols),
            "data": [
                {
                    "id": s.id,
                    "symbol": s.symbol,
                    "name": s.name,
                    "market": s.market,
                    "category": s.category,
                    "is_active": bool(s.is_active),
                }
                for s in symbols
            ]
        }
    finally:
        session.close()


@app.post("/api/symbols")
def add_symbol(symbol_data: SymbolCreate):
    """添加监控标的"""
    session = get_session()
    try:
        # 检查是否已存在
        existing = session.query(Symbol).filter(Symbol.symbol == symbol_data.symbol).first()
        if existing:
            raise HTTPException(status_code=400, detail="标的已存在")
        
        new_symbol = Symbol(**symbol_data.dict())
        session.add(new_symbol)
        session.commit()
        
        return {"message": "添加成功", "id": new_symbol.id}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@app.delete("/api/symbols/{symbol_id}")
def delete_symbol(symbol_id: int):
    """删除监控标的"""
    session = get_session()
    try:
        symbol = session.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise HTTPException(status_code=404, detail="标的不存在")
        
        session.delete(symbol)
        session.commit()
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ============ 工具接口 ============

@app.get("/api/generate/{report_type}")
def generate_report_now(report_type: str):
    """手动生成报告（测试用）"""
    try:
        generator = ReportGenerator()
        
        if report_type == 'noon':
            content = generator.generate_noon_report()
        elif report_type == 'daily':
            content = generator.generate_daily_report()
        else:
            raise HTTPException(status_code=400, detail="无效的报告类型")
        
        generator.save_report(content, report_type=report_type)
        
        return {
            "message": "报告生成成功",
            "report_type": report_type,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ============ 启动 ============

if __name__ == '__main__':
    import uvicorn
    
    # 初始化数据库
    init_db()
    print("✓ 数据库初始化完成")
    
    uvicorn.run(app, host='0.0.0.0', port=8000)

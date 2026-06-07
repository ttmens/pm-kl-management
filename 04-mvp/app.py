from fastapi import FastAPI, Request, Header, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Any
import json
import uuid
from datetime import datetime

import models
from models import (
    get_db, init_db, BizKlItem, SysKlItem, KlLink, AuditLog, User,
    get_user, audit,
    create_biz, get_biz, list_biz, update_biz, submit_biz, publish_biz, reject_biz,
    create_sys, get_sys, list_sys, update_sys,
    create_link, delete_link, get_links_for_biz, get_links_for_sys,
    list_audit, import_biz_from_markdown,
)

app = FastAPI(title="产品知识平台 MVP")
templates = Jinja2Templates(directory="templates")

# Ensure db is initialized on startup
@app.on_event("startup")
def startup():
    init_db()


# ===== Pydantic Models =====

class BizCreateRequest(BaseModel):
    name: str
    description: str = ""
    type: str
    tags: List[str] = []

class BizUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = None

class SysCreateRequest(BaseModel):
    name: str
    description: str = ""
    layer: str
    file_path: str = ""

class SysUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layer: Optional[str] = None
    file_path: Optional[str] = None

class LinkRequest(BaseModel):
    biz_id: str

class PackageResponse(BaseModel):
    version: str
    generated_at: str
    biz_kl: List[dict]
    sys_kl: List[dict]
    links: List[dict]
    lineage: dict

class ImportRequest(BaseModel):
    content: str

class RejectRequest(BaseModel):
    reason: str = ""


# ===== biz_kl API =====

@app.post("/api/biz")
def api_biz_create(req: BizCreateRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        item = create_biz(db, req.name, req.description, req.type, req.tags, x_user_id)
        return JSONResponse({"id": item.id, "name": item.name, "status": item.status})
    finally:
        db.close()

@app.get("/api/biz")
def api_biz_list(status: Optional[str] = None, q: Optional[str] = None):
    db = get_db()
    try:
        items = list_biz(db, status, q)
        return [{"id": i.id, "name": i.name, "type": i.type, "status": i.status, "tags": i.tags, "version": i.version, "updated_at": i.updated_at} for i in items]
    finally:
        db.close()

@app.get("/api/biz/{item_id}")
def api_biz_detail(item_id: str):
    db = get_db()
    try:
        item = get_biz(db, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        linked_sys = get_links_for_biz(db, item_id)
        return {
            "id": item.id, "name": item.name, "description": item.description,
            "type": item.type, "tags": item.tags, "status": item.status,
            "version": item.version, "created_by": item.created_by,
            "created_at": item.created_at, "updated_at": item.updated_at,
            "linked_sys": [{"id": s.id, "name": s.name, "layer": s.layer, "file_path": s.file_path} for s in linked_sys],
        }
    finally:
        db.close()

@app.put("/api/biz/{item_id}")
def api_biz_update(item_id: str, req: BizUpdateRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        item = update_biz(db, item_id, req.name, req.description, req.type, req.tags, x_user_id)
        if not item:
            raise HTTPException(404, "Not found")
        return {"id": item.id, "version": item.version}
    finally:
        db.close()

@app.post("/api/biz/{item_id}/submit")
def api_biz_submit(item_id: str, x_user_id: str = Header(...)):
    db = get_db()
    try:
        item = submit_biz(db, item_id, x_user_id)
        if not item:
            raise HTTPException(400, "Cannot submit")
        return {"id": item.id, "status": item.status}
    finally:
        db.close()

@app.post("/api/biz/{item_id}/publish")
def api_biz_publish(item_id: str, x_user_id: str = Header(...)):
    db = get_db()
    try:
        user = get_user(db, x_user_id)
        if not user or user.role != "admin":
            raise HTTPException(403, "Admin required")
        item = publish_biz(db, item_id, x_user_id)
        if not item:
            raise HTTPException(400, "Cannot publish")
        return {"id": item.id, "status": item.status}
    finally:
        db.close()


# ===== sys_kl API =====

@app.post("/api/sys")
def api_sys_create(req: SysCreateRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        item = create_sys(db, req.name, req.description, req.layer, req.file_path, x_user_id)
        return JSONResponse({"id": item.id, "name": item.name, "status": item.status})
    finally:
        db.close()

@app.get("/api/sys")
def api_sys_list(layer: Optional[str] = None, q: Optional[str] = None):
    db = get_db()
    try:
        items = list_sys(db, layer, q)
        return [{"id": i.id, "name": i.name, "layer": i.layer, "file_path": i.file_path, "status": i.status, "updated_at": i.updated_at} for i in items]
    finally:
        db.close()

@app.get("/api/sys/{item_id}")
def api_sys_detail(item_id: str):
    db = get_db()
    try:
        item = get_sys(db, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        linked_bz = get_links_for_sys(db, item_id)
        return {
            "id": item.id, "name": item.name, "description": item.description,
            "layer": item.layer, "file_path": item.file_path, "status": item.status,
            "created_by": item.created_by, "created_at": item.created_at, "updated_at": item.updated_at,
            "linked_biz": [{"id": b.id, "name": b.name, "type": b.type, "status": b.status} for b in linked_bz],
        }
    finally:
        db.close()

@app.put("/api/sys/{item_id}")
def api_sys_update(item_id: str, req: SysUpdateRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        item = update_sys(db, item_id, req.name, req.description, req.layer, req.file_path, x_user_id)
        if not item:
            raise HTTPException(404, "Not found")
        return {"id": item.id}
    finally:
        db.close()

@app.post("/api/sys/{item_id}/link")
def api_sys_link(item_id: str, req: LinkRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        link = create_link(db, item_id, req.biz_id, x_user_id)
        if not link:
            raise HTTPException(404, "biz_id not found")
        return {"id": link.id}
    finally:
        db.close()

@app.delete("/api/sys/{item_id}/link/{link_id}")
def api_sys_unlink(item_id: str, link_id: str, x_user_id: str = Header(...)):
    db = get_db()
    try:
        ok = delete_link(db, item_id, link_id, x_user_id)
        if not ok:
            raise HTTPException(404, "Link not found")
        return {"deleted": True}
    finally:
        db.close()


# ===== Audit API =====

@app.get("/api/audit")
def api_audit_list(item_id: Optional[str] = None, actor_id: Optional[str] = None, from_: Optional[str] = Query(None, alias="from"), to: Optional[str] = None):
    db = get_db()
    try:
        logs = list_audit(db, item_id, actor_id, from_, to)
        return [{"id": l.id, "item_type": l.item_type, "item_id": l.item_id, "action": l.action, "actor_id": l.actor_id, "created_at": l.created_at} for l in logs]
    finally:
        db.close()


# ===== Import API =====

@app.post("/api/import/biz")
def api_import_biz(req: ImportRequest, x_user_id: str = Header(...)):
    db = get_db()
    try:
        items = import_biz_from_markdown(db, req.content, x_user_id)
        return {"count": len(items), "ids": [i.id for i in items]}
    finally:
        db.close()


# ===== Package API =====

@app.get("/api/packages")
def api_package_json(biz_ids: str = Query(...)):
    db = get_db()
    try:
        ids = [i.strip() for i in biz_ids.split(",") if i.strip()]
        biz_items = []
        sys_items = []
        links = []
        lineage = {}

        for bid in ids:
            biz = get_biz(db, bid)
            if not biz or biz.status != "published":
                continue
            biz_items.append({
                "id": biz.id, "name": biz.name, "type": biz.type,
                "description": biz.description, "tags": biz.tags,
                "status": biz.status, "version": biz.version,
            })
            lineage[bid] = {"created_by": biz.created_by, "created_at": biz.created_at}

            linked_sys = get_links_for_biz(db, bid)
            for s in linked_sys:
                if s.status == "published":
                    sys_items.append({
                        "id": s.id, "name": s.name, "layer": s.layer,
                        "description": s.description, "file_path": s.file_path,
                        "linked_biz": [bid],
                    })
                    links.append({"biz_id": bid, "sys_id": s.id})

        return {
            "version": "1.0",
            "generated_at": datetime.utcnow().isoformat(),
            "biz_kl": biz_items,
            "sys_kl": sys_items,
            "links": links,
            "lineage": lineage,
        }
    finally:
        db.close()

@app.get("/api/packages/{biz_ids}.md")
def api_package_md(biz_ids: str):
    db = get_db()
    try:
        ids = [i.strip() for i in biz_ids.split(",") if i.strip()]
        lines = ["# 知识包\n", f"生成时间: {datetime.utcnow().isoformat()}\n"]

        for bid in ids:
            biz = get_biz(db, bid)
            if not biz or biz.status != "published":
                continue
            lines.append(f"\n## {biz.name}\n")
            lines.append(f"类型: {biz.type}\n")
            if biz.tags:
                lines.append(f"标签: {', '.join(biz.tags)}\n")
            lines.append(f"\n{biz.description}\n")

            linked_sys = get_links_for_biz(db, bid)
            if linked_sys:
                lines.append("\n### 关联代码模块\n")
                lines.append("| 名称 | 层级 | 路径 |\n")
                lines.append("|------|------|------|\n")
                for s in linked_sys:
                    lines.append(f"| {s.name} | {s.layer} | {s.file_path or '-'} |\n")

        return HTMLResponse(content="\n".join(lines), media_type="text/markdown")
    finally:
        db.close()


# ===== HTML Page Routes =====

@app.get("/", response_class=HTMLResponse)
async def page_index(request: Request, q: Optional[str] = None, tab: str = "biz"):
    db = get_db()
    try:
        biz_items = list_biz(db, q=q) if tab == "biz" else []
        sys_items = list_sys(db, q=q) if tab == "sys" else []
        return templates.TemplateResponse("index.html", {
            "request": request, "biz_items": biz_items, "sys_items": sys_items,
            "tab": tab, "q": q or "", "json": json,
        })
    finally:
        db.close()

@app.get("/biz", response_class=HTMLResponse)
async def page_biz_list(request: Request, q: Optional[str] = None, status: Optional[str] = None):
    db = get_db()
    try:
        items = list_biz(db, status, q)
        return templates.TemplateResponse("biz_list.html", {
            "request": request, "items": items, "q": q or "", "status": status or "", "json": json,
        })
    finally:
        db.close()

@app.get("/sys", response_class=HTMLResponse)
async def page_sys_list(request: Request, q: Optional[str] = None, layer: Optional[str] = None):
    db = get_db()
    try:
        items = list_sys(db, layer, q)
        return templates.TemplateResponse("sys_list.html", {
            "request": request, "items": items, "q": q or "", "layer": layer or "",
        })
    finally:
        db.close()

@app.get("/biz/{item_id}", response_class=HTMLResponse)
async def page_biz_detail(request: Request, item_id: str):
    db = get_db()
    try:
        item = get_biz(db, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        linked_sys = get_links_for_biz(db, item_id)
        return templates.TemplateResponse("biz_detail.html", {
            "request": request, "item": item, "linked_sys": linked_sys, "json": json,
        })
    finally:
        db.close()

@app.get("/sys/{item_id}", response_class=HTMLResponse)
async def page_sys_detail(request: Request, item_id: str):
    db = get_db()
    try:
        item = get_sys(db, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        linked_biz = get_links_for_sys(db, item_id)
        return templates.TemplateResponse("sys_detail.html", {
            "request": request, "item": item, "linked_biz": linked_biz,
        })
    finally:
        db.close()

@app.get("/export", response_class=HTMLResponse)
async def page_export(request: Request):
    db = get_db()
    try:
        biz_items = list_biz(db, status="published")
        return templates.TemplateResponse("export.html", {
            "request": request, "items": biz_items,
        })
    finally:
        db.close()

@app.get("/audit", response_class=HTMLResponse)
async def page_audit(request: Request, item_id: Optional[str] = None, actor_id: Optional[str] = None, from_: Optional[str] = Query(None, alias="from"), to: Optional[str] = None, x_user_id: str = Header(default="user-expert-001")):
    db = get_db()
    try:
        user = get_user(db, x_user_id)
        if not user or user.role != "admin":
            raise HTTPException(403, "仅管理员可查看审计日志")
        logs = list_audit(db, item_id, actor_id, from_, to)
        return templates.TemplateResponse("audit.html", {
            "request": request, "logs": logs, "item_id": item_id or "", "actor_id": actor_id or "", "from_": from_ or "", "to": to or "",
        })
    finally:
        db.close()

@app.get("/import", response_class=HTMLResponse)
async def page_import(request: Request):
    return templates.TemplateResponse("import.html", {"request": request})


# ===== HTML snippets for HTMX =====

@app.get("/hx/biz-list")
def hx_biz_list(request: Request, q: Optional[str] = None, status: Optional[str] = None):
    db = get_db()
    try:
        items = list_biz(db, status, q)
        return templates.TemplateResponse("biz_list.html", {
            "request": request, "items": items, "q": q or "", "status": status or "", "json": json,
        })
    finally:
        db.close()

@app.get("/hx/sys-list")
def hx_sys_list(request: Request, q: Optional[str] = None, layer: Optional[str] = None):
    db = get_db()
    try:
        items = list_sys(db, layer, q)
        return templates.TemplateResponse("sys_list.html", {
            "request": request, "items": items, "q": q or "", "layer": layer or "",
        })
    finally:
        db.close()

@app.get("/hx/audit-list")
def hx_audit_list(request: Request, item_id: Optional[str] = None, actor_id: Optional[str] = None, from_: Optional[str] = Query(None, alias="from"), to: Optional[str] = None):
    db = get_db()
    try:
        logs = list_audit(db, item_id, actor_id, from_, to)
        return templates.TemplateResponse("audit.html", {
            "request": request, "logs": logs, "item_id": item_id or "", "actor_id": actor_id or "", "from_": from_ or "", "to": to or "",
        })
    finally:
        db.close()

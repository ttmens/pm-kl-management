import models
import json

models.init_db()
db = models.get_db()

## Clear existing data (respect FK order)
db.execute("PRAGMA foreign_keys = OFF")
db.execute("DELETE FROM audit_logs")
db.execute("DELETE FROM kl_links")
db.execute("DELETE FROM biz_kl_items")
db.execute("DELETE FROM sys_kl_items")
db.execute("DELETE FROM users")
db.execute("PRAGMA foreign_keys = ON")
db.commit()

users = [
    ("user-admin-001", "管理员", "admin"),
    ("user-expert-001", "领域专家", "expert"),
    ("user-dev-001", "开发者", "developer"),
]
for u in users:
    db.execute("INSERT INTO users (id, name, role) VALUES (?, ?, ?)", u)
db.commit()

## Create biz_kl items
biz_items_data = [
    ("订单处理流程", "用户下单后的完整处理逻辑，包括库存校验、支付处理、物流分配。", "流程", ["订单", "支付", "物流"], "user-expert-001"),
    ("库存扣减规则", "库存扣减必须遵循先进先出原则，且不允许超卖。", "规则", ["库存", "规则"], "user-expert-001"),
    ("支付网关概念", "支付网关是连接商户系统与银行/第三方支付机构的中间件。", "概念", ["支付"], "user-expert-001"),
    ("退货退款流程", "用户发起退货申请，仓库确认收货后退还相应金额。", "流程", ["售后"], "user-expert-001"),
    ("用户权限概念", "系统通过RBAC模型控制用户访问不同模块的权限。", "概念", ["权限", "安全"], "user-expert-001"),
]

biz_ids = []
for name, desc, typ, tags, creator in biz_items_data:
    item = models.create_biz(db, name, desc, typ, tags, creator)
    biz_ids.append(item.id)
    # Publish some items
    models.submit_biz(db, item.id, creator)
    models.publish_biz(db, item.id, "user-admin-001")

db.commit()

## Create sys_kl items
sys_items_data = [
    ("order-service", "订单核心服务，处理订单生命周期管理", "domain", "app/order/domain/order_service.py", "user-dev-001"),
    ("payment-gateway", "支付网关接口封装", "application", "app/payment/gateway.py", "user-dev-001"),
    ("inventory-repository", "库存数据访问层", "infrastructure", "app/inventory/repo.py", "user-dev-001"),
    ("auth-middleware", "身份验证中间件", "infrastructure", "app/auth/middleware.py", "user-dev-001"),
    ("order-controller", "订单API控制器", "application", "app/order/controller.py", "user-dev-001"),
]

sys_ids = []
for name, desc, layer, fp, creator in sys_items_data:
    item = models.create_sys(db, name, desc, layer, fp, creator)
    sys_ids.append(item.id)

db.commit()

## Create links
links = [
    (sys_ids[0], biz_ids[0]),  # order-service -> 订单处理流程
    (sys_ids[1], biz_ids[2]),  # payment-gateway -> 支付网关概念
    (sys_ids[2], biz_ids[1]),  # inventory-repository -> 库存扣减规则
    (sys_ids[3], biz_ids[4]),  # auth-middleware -> 用户权限概念
    (sys_ids[0], biz_ids[3]),  # order-service -> 退货退款流程
]
for sid, bid in links:
    models.create_link(db, sid, bid, "user-dev-001")

db.commit()
db.close()

print("Seed data inserted successfully!")
print(f"Users: {len(users)}")
print(f"biz_kl items: {len(biz_ids)}")
print(f"sys_kl items: {len(sys_ids)}")
print(f"Links: {len(links)}")

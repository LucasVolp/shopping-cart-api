from fastapi import FastAPI

from modules.cart.router import router as cart_router
from modules.category.router import router as category_router
from modules.order.router import router as order_router
from modules.payment.router import router as payment_router
from modules.product.router import router as product_router
from modules.user.router import router as user_router

app = FastAPI(
    title="Shopping Cart API",
    description="API for managing a shopping cart",
    version="1.0.0",
)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])

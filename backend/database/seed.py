from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.allowed_user import AllowedUser
from models.product import Product
from models.product_detail import ProductDetail

ALLOWED_USERS = [
    ("Ali Khan", "ali.khan.demo@gmail.com"),
    ("Ahmed Ali", "ahmed.ali.demo@gmail.com"),
    ("Sara Ahmed", "sara.ahmed.demo@gmail.com"),
    ("Hassan Raza", "hassan.raza.demo@gmail.com"),
    ("Fatima Noor", "fatima.noor.demo@gmail.com"),
    ("Bilal Sheikh", "bilal.sheikh.demo@gmail.com"),
    ("Ayesha Khan", "ayesha.khan.demo@gmail.com"),
    ("Usman Malik", "usman.malik.demo@gmail.com"),
    ("Zain Ali", "zain.ali.demo@gmail.com"),
    ("Maryam Ahmed", "maryam.ahmed.demo@gmail.com"),
    ("Bashar Tariq", "bashartc14@gmail.com"),
    ("Saad", "bashartech56@gmail.com"),
]

PRODUCTS = [
    {
        "product_name": "Laptop Pro 15",
        "category": "Laptops",
        "description": "High-performance laptop for professionals with 32GB RAM and 1TB SSD.",
        "price": 1499.99,
        "stock": 25,
        "manufacturer": "TechPro",
        "specifications": "Intel Core i7, 32GB DDR5 RAM, 1TB NVMe SSD, 15.6\" 4K Display",
        "warranty": "2 Years",
        "country": "USA",
        "weight": 1.8,
    },
    {
        "product_name": "Wireless Mouse MX",
        "category": "Accessories",
        "description": "Ergonomic wireless mouse with 6 programmable buttons.",
        "price": 79.99,
        "stock": 150,
        "manufacturer": "LogiTech",
        "specifications": "6 buttons, 4000 DPI, USB-C charging, 70hr battery",
        "warranty": "1 Year",
        "country": "China",
        "weight": 0.1,
    },
    {
        "product_name": "Mechanical Keyboard RGB",
        "category": "Accessories",
        "description": "Full-size mechanical keyboard with customizable RGB lighting.",
        "price": 129.99,
        "stock": 80,
        "manufacturer": "KeyCraft",
        "specifications": "Cherry MX Blue switches, per-key RGB, aluminum frame",
        "warranty": "2 Years",
        "country": "Taiwan",
        "weight": 0.9,
    },
    {
        "product_name": "27\" 4K Monitor",
        "category": "Monitors",
        "description": "Ultra-sharp 4K monitor perfect for design and development.",
        "price": 499.99,
        "stock": 40,
        "manufacturer": "ViewPulse",
        "specifications": "27\" IPS, 3840x2160, 60Hz, HDR400, USB-C hub",
        "warranty": "3 Years",
        "country": "South Korea",
        "weight": 5.2,
    },
    {
        "product_name": "USB-C Hub 7-in-1",
        "category": "Accessories",
        "description": "Compact USB-C hub with HDMI, SD card, and USB-A ports.",
        "price": 39.99,
        "stock": 200,
        "manufacturer": "PortBliss",
        "specifications": "HDMI 4K, 2x USB-A 3.0, SD/microSD, PD 100W, Ethernet",
        "warranty": "1 Year",
        "country": "China",
        "weight": 0.08,
    },
    {
        "product_name": "Noise Cancelling Headphones",
        "category": "Audio",
        "description": "Premium over-ear headphones with active noise cancellation.",
        "price": 299.99,
        "stock": 60,
        "manufacturer": "SoundWave",
        "specifications": "ANC, 40hr battery, Bluetooth 5.3, 40mm drivers",
        "warranty": "2 Years",
        "country": "Denmark",
        "weight": 0.25,
    },
    {
        "product_name": "Webcam 4K Stream",
        "category": "Accessories",
        "description": "Professional 4K webcam with auto-focus and built-in microphone.",
        "price": 199.99,
        "stock": 35,
        "manufacturer": "ClearView",
        "specifications": "4K@30fps, 1080p@60fps, auto-focus, dual mics, FOV 90",
        "warranty": "1 Year",
        "country": "USA",
        "weight": 0.15,
    },
    {
        "product_name": "Smart Desk Lamp",
        "category": "Lighting",
        "description": "LED desk lamp with wireless charger and adjustable color temperature.",
        "price": 89.99,
        "stock": 100,
        "manufacturer": "LumiTech",
        "specifications": "15W Qi charging, 5 brightness levels, 3000-6500K",
        "warranty": "1 Year",
        "country": "China",
        "weight": 1.2,
    },
    {
        "product_name": "External SSD 1TB",
        "category": "Storage",
        "description": "Portable external SSD with high-speed USB-C interface.",
        "price": 109.99,
        "stock": 120,
        "manufacturer": "FastStore",
        "specifications": "1TB, 1050MB/s read, 1000MB/s write, IP55",
        "warranty": "3 Years",
        "country": "Taiwan",
        "weight": 0.04,
    },
    {
        "product_name": "Ergonomic Standing Desk",
        "category": "Furniture",
        "description": "Electric height-adjustable standing desk with memory presets.",
        "price": 599.99,
        "stock": 15,
        "manufacturer": "ErgoLife",
        "specifications": "140x70cm, 72-120cm height, 4 memory presets, 80kg load",
        "warranty": "5 Years",
        "country": "Germany",
        "weight": 28.0,
    },
    {
        "product_name": "Graphics Tablet Pro",
        "category": "Accessories",
        "description": "Digital drawing tablet with pressure-sensitive stylus.",
        "price": 349.99,
        "stock": 20,
        "manufacturer": "DrawPro",
        "specifications": "10\"x6\", 8192 pressure levels, wireless stylus, 8 shortcuts",
        "warranty": "2 Years",
        "country": "Japan",
        "weight": 0.45,
    },
    {
        "product_name": "Portable Bluetooth Speaker",
        "category": "Audio",
        "description": "Waterproof portable speaker with 360-degree sound.",
        "price": 59.99,
        "stock": 90,
        "manufacturer": "SoundWave",
        "specifications": "IP67, 20hr battery, Bluetooth 5.3, 30W output",
        "warranty": "1 Year",
        "country": "China",
        "weight": 0.6,
    },
    {
        "product_name": "Server Rack UPS 1500VA",
        "category": "Networking",
        "description": "Uninterruptible power supply for server racks.",
        "price": 899.99,
        "stock": 8,
        "manufacturer": "PowerGuard",
        "specifications": "1500VA/900W, 8 outlets, LCD, AVR, 10min at full load",
        "warranty": "3 Years",
        "country": "USA",
        "weight": 15.0,
    },
    {
        "product_name": "Cloud Backup License - 1TB",
        "category": "Software",
        "description": "Annual cloud backup license with 1TB storage.",
        "price": 49.99,
        "stock": 500,
        "manufacturer": "CloudSafe",
        "specifications": "1TB storage, 256-bit encryption, 30-day version history",
        "warranty": "N/A",
        "country": "USA",
        "weight": 0.0,
    },
    {
        "product_name": "VPN Business Plan - 10 Seats",
        "category": "Software",
        "description": "Business VPN plan for 10 users with dedicated servers.",
        "price": 299.99,
        "stock": 100,
        "manufacturer": "SecureTunnel",
        "specifications": "10 users, dedicated servers, 5Gbps, 24/7 support",
        "warranty": "N/A",
        "country": "USA",
        "weight": 0.0,
    },
]


async def seed_allowed_users(session: AsyncSession) -> None:
    for full_name, email in ALLOWED_USERS:
        result = await session.execute(
            select(AllowedUser).where(AllowedUser.email == email)
        )
        if not result.scalar_one_or_none():
            session.add(AllowedUser(full_name=full_name, email=email))
    await session.flush()


async def seed_products(session: AsyncSession) -> None:
    for item in PRODUCTS:
        result = await session.execute(
            select(Product).where(Product.product_name == item["product_name"])
        )
        if result.scalar_one_or_none():
            continue
        product = Product(
            product_name=item["product_name"],
            category=item["category"],
            description=item["description"],
            price=item["price"],
            stock=item["stock"],
            manufacturer=item["manufacturer"],
        )
        session.add(product)
        await session.flush()
        detail = ProductDetail(
            product_id=product.id,
            specifications=item["specifications"],
            warranty=item["warranty"],
            country=item["country"],
            weight=item["weight"],
        )
        session.add(detail)
    await session.flush()


async def seed_database(session: AsyncSession) -> None:
    await seed_allowed_users(session)
    await seed_products(session)
    await session.commit()

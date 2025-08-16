from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import random

# Resource باسم الخدمة
resource = Resource(attributes={"service.name": "api1-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # instrumentation حقيقية للـ Flask

@app.route("/order")
def order():
    order_id = f"ord-{random.randint(1000,9999)}"
    user_id = f"user-{random.randint(1,10)}"
    amount = random.randint(50,500)

    # Span رئيسي للعملية
    with tracer.start_as_current_span("manual_order_process") as span_main:
        span_main.set_attribute("order.id", order_id)
        span_main.set_attribute("user.id", user_id)
        span_main.set_attribute("order.amount", amount)

        # Span فرعي: التحقق من المخزون
        with tracer.start_as_current_span("check_inventory") as span_inv:
            span_inv.set_attribute("items.available", True)

        # Span فرعي: احتساب الضريبة
        with tracer.start_as_current_span("calculate_tax") as span_tax:
            span_tax.set_attribute("tax.amount", round(amount*0.15,2))

        # Span فرعي: إنشاء الفاتورة
        with tracer.start_as_current_span("generate_invoice") as span_invoice:
            span_invoice.set_attribute("invoice.id", f"inv-{random.randint(1000,9999)}")

        return jsonify({
            "message": "Order processed with real tracing!",
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

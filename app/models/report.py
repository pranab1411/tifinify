from datetime import datetime
from app.models import db


class Report(db.Model):
    """User-submitted dispute and moderation ticket."""
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id", ondelete="CASCADE"), nullable=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=True)
    report_type = db.Column(db.String(50), nullable=False)  # 'incorrect_info', 'fake_pricing', 'inappropriate_content', 'suspicious_review', 'closed_provider'
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)  # 'pending', 'reviewed', 'resolved', 'dismissed'
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider_id": self.provider_id,
            "review_id": self.review_id,
            "report_type": self.report_type,
            "description": self.description,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "created_at": self.created_at.strftime("%b %d, %Y") if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Report id={self.id} type={self.report_type} status={self.status}>"


class AdminAuditLog(db.Model):
    """Security audit log for administrative actions."""
    __tablename__ = "admin_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AdminAuditLog action={self.action} target={self.target_type}:{self.target_id}>"

from services.report_service import ReportService


class ReportController:
    @staticmethod
    def summary_report():
        return ReportService.summary()

    @staticmethod
    def user_report(user_id):
        return ReportService.user_report(user_id)

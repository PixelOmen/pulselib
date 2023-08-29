class ReportEnum:
    scheduling = "scheduling"
    operations = "operations"

    @classmethod
    def choices(cls):
        return (
            "scheduling",
            "operations",
        )

    def __init__(self) -> None:
        raise NotImplementedError("ReportEnum class should not be instantiated.")
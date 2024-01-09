class ReportEnum:
    scheduling = "scheduling"
    operations = "operations"
    it = "it"

    @classmethod
    def choices(cls):
        return (
            "scheduling",
            "operations",
            "it"
        )

    def __init__(self) -> None:
        raise NotImplementedError("ReportEnum class should not be instantiated.")
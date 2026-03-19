class EcosystemMeta(type):
    """
    Базовый метакласс экосистемы.
    • Автоматически регистрирует каждый конкретный подкласс в глобальном реестре.
    • Предоставляет API для получения реестра и поиска по имени.
    """

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases and not namespace.get("_abstract", False):
            EcosystemMeta._registry[name] = cls
            print(f"[EcosystemMeta] Зарегистрирован класс: {name}")
        return cls

    @classmethod
    def get_registry(mcs):
        return dict(mcs._registry)

    @classmethod
    def get_by_name(mcs, name):
        return mcs._registry.get(name)

document.addEventListener('DOMContentLoaded', function () {
    let isMetric = true;
    const toggleBtn = document.getElementById('unit-toggle');
    if (!toggleBtn) return;

    function render() {
        document.querySelectorAll('.temp-value').forEach(el => {
            const c = parseFloat(el.dataset.c);
            if (Number.isNaN(c)) return;
            el.textContent = isMetric
                ? `${c}°C`
                : `${Math.round((c * 9 / 5 + 32) * 10) / 10}°F`;
        });

        document.querySelectorAll('.speed-value').forEach(el => {
            const kmh = parseFloat(el.dataset.kmh);
            if (Number.isNaN(kmh)) return;
            el.textContent = isMetric
                ? `${kmh} km/h`
                : `${Math.round(kmh * 0.621371 * 10) / 10} mph`;
        });
    }

    toggleBtn.addEventListener('click', function () {
        isMetric = !isMetric;
        render();
    });
});

async function loadIncludes() {
    const includes = document.querySelectorAll('[data-include]');
    
    const tasks = [...includes].map(async (el) => {
        const path = el.getAttribute('data-include');
        try {
            const response = await fetch(path);
            if (!response.ok) throw new Error(`Ошибка загрузки ${path}`);
            el.innerHTML = await response.text();
        } catch (err) {
            console.error('[includes]', err);
        }
    });

    await Promise.all(tasks);
}
loadIncludes().then(() => {
    if (typeof initAuth === 'function') {
        initAuth();
    }
});
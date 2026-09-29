document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    const searchForm = document.querySelector('.project-search');
    const searchInput = document.getElementById('project-search-input');
    const clearLink = document.getElementById('projects-clear');
    const loading = document.getElementById('projects-loading');
    const error = document.getElementById('projects-error');
    const empty = document.getElementById('projects-empty');
    const retryButton = document.getElementById('projects-retry');
    const emptyClearLink = document.getElementById('projects-empty-clear');
    const emptyAddLink = document.getElementById('projects-empty-add');
    const urlPlaceholder = '00000000-0000-0000-0000-000000000000';
    let requestNumber = 0;

    function element(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function safeHttpUrl(value) {
        if (!value) return '';
        try {
            const url = new URL(value);
            return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
        } catch {
            return '';
        }
    }

    function projectActionUrl(template, id) {
        return template.replace(urlPlaceholder, encodeURIComponent(id));
    }

    function csrfInput() {
        const input = element('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = grid.dataset.csrfToken;
        return input;
    }

    function starForm(project) {
        const form = element('form', 'project-star');
        form.method = 'post';
        form.action = projectActionUrl(grid.dataset.starUrlTemplate, project.id);
        form.append(csrfInput());

        const button = element('button', 'project-star__button');
        button.type = 'submit';
        if (project.is_starred) {
            button.classList.add('project-star__button--starred');
            button.setAttribute('aria-label', `Unstar ${project.title}`);
            button.title = 'Unstar this project';
        } else {
            const action = grid.dataset.isAuthenticated === 'true' ? 'Star' : 'Sign in to star';
            button.setAttribute('aria-label', `${action} ${project.title}`);
        }
        button.append(
            element('span', 'project-star__icon', project.is_starred ? '\u2605' : '\u2606'),
            element('span', '', project.is_starred ? 'Starred' : 'Star'),
            element('span', 'project-star__count', String(project.star_count)),
        );
        button.querySelector('.project-star__icon').setAttribute('aria-hidden', 'true');
        form.append(button);
        return form;
    }

    function deleteControls(project) {
        const id = `delete-project-${project.id}`;
        const titleId = `delete-title-${project.id}`;
        const trigger = element('button', 'button button-danger-outline', 'Delete');
        trigger.type = 'button';
        trigger.setAttribute('popovertarget', id);
        trigger.setAttribute('aria-label', `Delete ${project.title}`);

        const modal = element('div', 'project-delete-modal');
        modal.id = id;
        modal.setAttribute('popover', 'auto');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', titleId);

        const backdrop = element('button', 'project-delete-modal__backdrop');
        backdrop.type = 'button';
        backdrop.setAttribute('popovertarget', id);
        backdrop.setAttribute('popovertargetaction', 'hide');
        backdrop.setAttribute('aria-label', 'Close delete confirmation');

        const content = element('div', 'project-delete-modal__content glass-surface');
        const close = element('button', 'project-delete-modal__close', '\u00D7');
        close.type = 'button';
        close.setAttribute('popovertarget', id);
        close.setAttribute('popovertargetaction', 'hide');
        close.setAttribute('aria-label', 'Close delete confirmation');

        const heading = element('h2', '', 'Let this project go?');
        heading.id = titleId;
        const question = element('p');
        question.append('Are you sure you want to delete ', element('strong', '', project.title), '? This action cannot be undone.');

        const actions = element('div', 'project-delete-modal__actions');
        const keep = element('button', 'button button-secondary', 'Keep It');
        keep.type = 'button';
        keep.setAttribute('popovertarget', id);
        keep.setAttribute('popovertargetaction', 'hide');

        const form = element('form');
        form.method = 'post';
        form.action = projectActionUrl(grid.dataset.deleteUrlTemplate, project.id);
        const confirm = element('button', 'button button-danger', 'Yes, Delete');
        confirm.type = 'submit';
        form.append(csrfInput(), confirm);
        actions.append(keep, form);
        content.append(close, element('p', 'eyebrow', 'Delete project'), heading, question, actions);
        modal.append(backdrop, content);
        return [trigger, modal];
    }

    function projectCard(project) {
        const card = element('article', 'project-card glass-surface');
        const titleId = `project-${project.id}`;
        card.setAttribute('aria-labelledby', titleId);

        const thumbnailUrl = safeHttpUrl(project.thumbnail);
        if (thumbnailUrl) {
            const image = element('img', 'project-thumbnail');
            image.src = thumbnailUrl;
            image.alt = `Preview of ${project.title}`;
            image.loading = 'lazy';
            image.width = 640;
            image.height = 360;
            card.append(image);
        } else {
            const placeholder = element('div', 'project-placeholder');
            placeholder.setAttribute('aria-hidden', 'true');
            placeholder.append(
                element('span', 'project-placeholder-mark', Array.from(project.title)[0] || '\u2726'),
                element('span', '', project.category_display),
            );
            card.append(placeholder);
        }

        const content = element('div', 'project-content');
        const badges = element('div', 'project-badges');
        badges.append(element('span', 'project-category', project.category_display));
        if (project.is_featured) badges.append(element('span', 'featured-badge', 'Featured'));

        const title = element('h2', '', project.title);
        title.id = titleId;
        const details = element('dl', 'project-details');
        const role = element('div', 'project-role');
        role.append(element('dt', '', 'My role'), element('dd', '', project.role));
        const skills = element('div', 'project-skills');
        skills.append(element('dt', '', 'Skills'), element('dd', '', project.skills));
        details.append(role, skills);

        const actions = element('div', 'project-card-actions');
        const projectUrl = safeHttpUrl(project.project_url);
        if (projectUrl) {
            const link = element('a', 'button', 'View Project');
            link.href = projectUrl;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.setAttribute('aria-label', `View Project: ${project.title} (opens in a new tab)`);
            const arrow = element('span', '', '\u2197');
            arrow.setAttribute('aria-hidden', 'true');
            link.append(arrow);
            actions.append(link);
        }
        actions.append(starForm(project));
        if (grid.dataset.deleteUrlTemplate) actions.append(...deleteControls(project));

        content.append(badges, title, element('p', 'project-description', project.description), details, actions);
        card.append(content);
        return card;
    }

    function showState(state) {
        loading.hidden = state !== 'loading';
        error.hidden = state !== 'error';
        empty.hidden = state !== 'empty';
        grid.hidden = state !== 'ready';
    }

    function showEmpty(query) {
        document.getElementById('projects-empty-title').textContent = query
            ? 'No matching projects found.'
            : 'No projects have been added yet.';
        document.getElementById('projects-empty-message').textContent = query
            ? `We couldn't find a project titled \u201C${query}\u201D.`
            : 'A little space for the next idea.';
        emptyClearLink.hidden = !query;
        if (emptyAddLink) emptyAddLink.hidden = Boolean(query);
        showState('empty');
    }

    async function loadProjects(query = '') {
        const currentRequest = ++requestNumber;
        clearLink.hidden = !query;
        grid.replaceChildren();
        showState('loading');

        try {
            const url = new URL(grid.dataset.apiUrl, window.location.origin);
            if (query) url.searchParams.set('title', query);
            const response = await fetch(url, { headers: { Accept: 'application/json' } });
            if (!response.ok) throw new Error(`Projects request failed: ${response.status}`);
            const projects = await response.json();
            if (!Array.isArray(projects)) throw new Error('Unexpected projects response');
            if (currentRequest !== requestNumber) return;

            if (projects.length === 0) {
                showEmpty(query);
            } else {
                grid.replaceChildren(...projects.map(projectCard));
                showState('ready');
            }
        } catch (fetchError) {
            if (currentRequest !== requestNumber) return;
            console.error('Could not load projects:', fetchError);
            showState('error');
        }
    }

    function updateSearch(query) {
        const url = new URL(window.location.href);
        if (query) url.searchParams.set('title', query);
        else url.searchParams.delete('title');
        window.history.pushState({}, '', url);
        loadProjects(query);
    }

    searchForm.addEventListener('submit', event => {
        event.preventDefault();
        updateSearch(searchInput.value.trim());
    });
    [clearLink, emptyClearLink].forEach(link => link.addEventListener('click', event => {
        event.preventDefault();
        searchInput.value = '';
        updateSearch('');
    }));
    retryButton.addEventListener('click', () => loadProjects(searchInput.value.trim()));
    window.addEventListener('popstate', () => {
        searchInput.value = new URLSearchParams(window.location.search).get('title') || '';
        loadProjects(searchInput.value.trim());
    });

    loadProjects(searchInput.value.trim());
});

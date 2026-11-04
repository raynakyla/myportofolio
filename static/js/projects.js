document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    const projectListUrl = grid.dataset.apiUrl;
    const projectDetailUrlTemplate = grid.dataset.detailUrlTemplate;
    const projectStarUrlTemplate = grid.dataset.starUrlTemplate;
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
    const categoryLabels = {
        web: 'Web Development',
        product: 'Product & UX',
        creative: 'Creative Work',
    };
    let requestNumber = 0;
    let listController = null;
    let searchTimeout = null;

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

    async function mutation(url, method, payload) {
        const headers = {
            Accept: 'application/json',
            'X-CSRFToken': grid.dataset.csrfToken,
        };
        if (payload !== undefined) headers['Content-Type'] = 'application/json';
        const response = await fetch(url, {
            method,
            credentials: 'same-origin',
            headers,
            ...(payload !== undefined ? { body: JSON.stringify(payload) } : {}),
        });
        const result = response.status === 204 ? null : await response.json().catch(() => null);
        return { response, result };
    }

    function errorMessage(result, fallback) {
        if (typeof result?.detail === 'string') return result.detail;
        if (typeof result?.message === 'string') return result.message;
        return fallback;
    }

    function starForm(project) {
        const form = element('form', 'project-star');
        form.method = 'post';
        form.action = projectActionUrl(projectStarUrlTemplate, project.id);

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
        form.addEventListener('submit', async event => {
            event.preventDefault();
            if (grid.dataset.isAuthenticated !== 'true') {
                showToast('Sign in required', 'Please sign in to star projects.', 'error');
                return;
            }
            button.disabled = true;
            try {
                const { response, result } = await mutation(form.action, 'POST');
                if (!response.ok) throw new Error(errorMessage(result, 'Could not update the star. Please try again.'));
                form.replaceWith(starForm(result));
                showToast(result.is_starred ? 'Project starred' : 'Star removed', project.title, 'success');
            } catch (error) {
                showToast('Star update failed', error.message || 'Please try again.', 'error');
                button.disabled = false;
            }
        });
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
        form.action = projectActionUrl(projectDetailUrlTemplate, project.id);
        const confirm = element('button', 'button button-danger', 'Yes, Delete');
        confirm.type = 'submit';
        form.append(confirm);
        form.addEventListener('submit', async event => {
            event.preventDefault();
            confirm.disabled = true;
            try {
                const { response, result } = await mutation(form.action, 'DELETE');
                if (!response.ok) throw new Error(errorMessage(result, 'Could not delete the project. Please try again.'));
                showToast('Project deleted', `"${project.title}" has been deleted.`, 'success');
                loadProjects(searchInput.value.trim());
            } catch (error) {
                showToast('Delete failed', error.message || 'Please try again.', 'error');
                confirm.disabled = false;
            }
        });
        actions.append(keep, form);
        content.append(close, element('p', 'eyebrow', 'Delete project'), heading, question, actions);
        modal.append(backdrop, content);
        return [trigger, modal];
    }

    function projectCard(project) {
        const card = element('article', 'project-card glass-surface');
        const titleId = `project-${project.id}`;
        const categoryDisplay = categoryLabels[project.category] || project.category;
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
                element('span', '', categoryDisplay),
            );
            card.append(placeholder);
        }

        const content = element('div', 'project-content');
        const badges = element('div', 'project-badges');
        badges.append(element('span', 'project-category', categoryDisplay));
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
        if (projectDetailUrlTemplate) actions.append(...deleteControls(project));

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
        if (listController) listController.abort();
        listController = new AbortController();
        clearLink.hidden = !query;
        grid.replaceChildren();
        showState('loading');

        try {
            const url = new URL(projectListUrl, window.location.origin);
            if (query) url.searchParams.set('title', query);
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
                signal: listController.signal,
            });
            if (!response.ok) throw new Error(`Projects request failed: ${response.status}`);
            const projects = await response.json();
            if (!Array.isArray(projects)) throw new Error('Unexpected projects response');
            if (currentRequest !== requestNumber) return;
            projects.sort((a, b) => Number(b.is_featured) - Number(a.is_featured)
                || a.title.localeCompare(b.title) || a.id.localeCompare(b.id));

            if (projects.length === 0) {
                showEmpty(query);
            } else {
                grid.replaceChildren(...projects.map(projectCard));
                showState('ready');
            }
        } catch (fetchError) {
            if (currentRequest !== requestNumber) return;
            if (fetchError.name === 'AbortError') return;
            console.error('Could not load projects:', fetchError);
            showState('error');
        } finally {
            if (currentRequest === requestNumber) listController = null;
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
        clearTimeout(searchTimeout);
        updateSearch(searchInput.value.trim());
    });
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => updateSearch(searchInput.value.trim()), 300);
    });
    [clearLink, emptyClearLink].forEach(link => link.addEventListener('click', event => {
        event.preventDefault();
        clearTimeout(searchTimeout);
        searchInput.value = '';
        updateSearch('');
    }));
    retryButton.addEventListener('click', () => loadProjects(searchInput.value.trim()));
    window.addEventListener('popstate', () => {
        clearTimeout(searchTimeout);
        searchInput.value = new URLSearchParams(window.location.search).get('title') || '';
        loadProjects(searchInput.value.trim());
    });

    const createModal = document.getElementById('project-create-modal');
    if (createModal) {
        const createForm = document.getElementById('project-create-form');
        const submitButton = document.getElementById('project-create-submit');
        const submitLabel = document.getElementById('project-create-submit-label');
        const generalError = document.getElementById('project-create-error-general');
        const closeButtons = createModal.querySelectorAll('[data-close-project-modal]');
        let submitting = false;
        let opener = null;
        let afterClose = null;

        function clearCreateErrors() {
            createForm.querySelectorAll('.form-error').forEach(node => {
                node.textContent = '';
                node.hidden = true;
            });
            createForm.querySelectorAll('[aria-invalid]').forEach(field => {
                field.removeAttribute('aria-invalid');
                field.removeAttribute('aria-errormessage');
            });
        }

        function showCreateError(message) {
            generalError.textContent = message;
            generalError.hidden = false;
        }

        function showCreateValidation(errors) {
            let firstInvalid = null;
            for (const [name, details] of Object.entries(errors)) {
                const message = (Array.isArray(details) ? details : [details])
                    .map(detail => typeof detail === 'string' ? detail : detail.message || String(detail))
                    .join(' ');
                const field = createForm.elements.namedItem(name);
                const errorNode = document.getElementById(`project-create-error-${name}`);
                if (name === 'non_field_errors' || !field || !errorNode) {
                    showCreateError(message);
                    continue;
                }
                errorNode.textContent = message;
                errorNode.hidden = false;
                field.setAttribute('aria-invalid', 'true');
                field.setAttribute('aria-errormessage', errorNode.id);
                if (!firstInvalid) firstInvalid = field;
            }
            if (firstInvalid) firstInvalid.focus();
        }

        function setSubmitting(value) {
            submitting = value;
            submitButton.disabled = value;
            submitLabel.textContent = value ? 'Adding project...' : 'Add project';
            createForm.setAttribute('aria-busy', String(value));
            closeButtons.forEach(button => { button.disabled = value; });
        }

        function closeCreateModal(force = false, callback = null) {
            if (!createModal.open || createModal.classList.contains('is-closing') || (submitting && !force)) return;
            afterClose = callback;
            createModal.classList.add('is-closing');
            const delay = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 180;
            window.setTimeout(() => {
                createModal.close();
                createModal.classList.remove('is-closing');
            }, delay);
        }

        [document.getElementById('project-create-open'), emptyAddLink].forEach(trigger => {
            if (!trigger) return;
            trigger.addEventListener('click', event => {
                event.preventDefault();
                if (createModal.open) return;
                opener = trigger;
                clearCreateErrors();
                createModal.showModal();
                createForm.elements.namedItem('title').focus();
            });
        });

        closeButtons.forEach(button => button.addEventListener('click', () => closeCreateModal()));
        createModal.addEventListener('click', event => {
            if (event.target === createModal) closeCreateModal();
        });
        createModal.addEventListener('cancel', event => {
            event.preventDefault();
            closeCreateModal();
        });
        createModal.addEventListener('close', () => {
            createForm.reset();
            clearCreateErrors();
            if (opener) opener.focus();
            if (afterClose) {
                const callback = afterClose;
                afterClose = null;
                callback();
            }
        });

        createForm.addEventListener('submit', async event => {
            event.preventDefault();
            if (submitting) return;
            clearCreateErrors();
            setSubmitting(true);

            try {
                const formData = new FormData(createForm);
                const payload = Object.fromEntries(
                    ['title', 'description', 'category', 'role', 'skills', 'thumbnail', 'project_url']
                        .map(name => [name, String(formData.get(name) ?? '')]),
                );
                const featured = createForm.elements.namedItem('is_featured');
                if (featured) payload.is_featured = featured.checked;
                const { response, result } = await mutation(createForm.action, 'POST', payload);

                if (response.status === 400 && result && typeof result === 'object') {
                    showCreateValidation(result);
                    showToast('Check project details', 'Please correct the highlighted fields.', 'error');
                    return;
                }
                if (!response.ok) {
                    throw new Error(errorMessage(result, 'Could not add the project. Please try again.'));
                }

                setSubmitting(false);
                closeCreateModal(true, () => {
                    showToast('Project added', `"${result.title}" has been added.`, 'success');
                    searchInput.value = '';
                    updateSearch('');
                });
            } catch (error) {
                const message = error instanceof TypeError
                    ? 'Could not connect. Please try again.'
                    : (error.message || 'Could not add the project. Please try again.');
                showCreateError(message);
                showToast('Could not add project', message, 'error');
            } finally {
                setSubmitting(false);
            }
        });
    }

    loadProjects(searchInput.value.trim());
});

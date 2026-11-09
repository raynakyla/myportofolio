document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('experience-grid');
    if (!grid) return;

    const searchForm = document.getElementById('experience-search');
    const searchInput = document.getElementById('experience-search-input');
    const clearLink = document.getElementById('experience-search-clear');
    const loading = document.getElementById('experience-loading');
    const error = document.getElementById('experience-error');
    const retryButton = document.getElementById('experience-retry');
    const empty = document.getElementById('experience-empty');
    const emptyTitle = document.getElementById('experience-empty-title');
    const emptyMessage = document.getElementById('experience-empty-message');
    const emptyAdd = document.getElementById('experience-empty-add');
    const deleteModals = document.getElementById('experience-delete-modals');
    const categoryLists = [...grid.querySelectorAll('[data-experience-category]')];
    const urlPlaceholder = '00000000-0000-0000-0000-000000000000';
    const isAuthenticated = grid.dataset.isAuthenticated === 'true';
    const isOwner = grid.dataset.isOwner === 'true';
    let experiences = [];
    let hasApiData = false;
    let listController = null;
    let requestNumber = 0;
    let searchTimeout = null;

    function element(tag, className, value) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (value !== undefined) node.textContent = value;
        return node;
    }

    function actionUrl(template, id) {
        return template.replace(urlPlaceholder, encodeURIComponent(id));
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

    function getCookie(name) {
        const cookie = document.cookie.split('; ').find(part => part.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : '';
    }

    function csrfToken() {
        return getCookie('csrftoken') || grid.dataset.csrfToken;
    }

    function loginUrl() {
        const url = new URL(grid.dataset.loginUrl, window.location.origin);
        url.searchParams.set('next', window.location.pathname + window.location.search);
        return url.href;
    }

    function formatDate(value) {
        if (!value) return '';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '';
        return new Intl.DateTimeFormat('en-US', {
            month: 'short', year: 'numeric', timeZone: 'UTC',
        }).format(date);
    }

    function errorMessage(result, fallback) {
        if (!result || typeof result !== 'object') return fallback;
        if (typeof result.detail === 'string') return result.detail;
        for (const [field, details] of Object.entries(result)) {
            const first = Array.isArray(details) ? details[0] : details;
            if (first) return `${field === 'non_field_errors' ? 'Details' : field}: ${String(first)}`;
        }
        return fallback;
    }

    async function mutation(url, method, payload) {
        const headers = {
            Accept: 'application/json',
            'X-CSRFToken': csrfToken(),
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

    function showMutationError(response, result, fallback) {
        const title = response.status === 403 ? 'Permission denied' : 'Experience update failed';
        showToast(title, errorMessage(result, fallback), 'error');
    }

    function starControl(experience) {
        const wrapper = element(isAuthenticated ? 'form' : 'div', 'project-star');
        if (isAuthenticated) {
            wrapper.method = 'post';
            wrapper.action = actionUrl(grid.dataset.starUrlTemplate, experience.id);
            const token = element('input');
            token.type = 'hidden';
            token.name = 'csrfmiddlewaretoken';
            token.value = csrfToken();
            wrapper.append(token);
        }

        const control = element(isAuthenticated ? 'button' : 'a', 'project-star__button');
        if (isAuthenticated) control.type = 'submit';
        else control.href = loginUrl();
        if (experience.is_starred) control.classList.add('project-star__button--starred');
        control.setAttribute(
            'aria-label',
            `${experience.is_starred ? 'Unstar' : isAuthenticated ? 'Star' : 'Sign in to star'} ${experience.title}`,
        );
        if (experience.is_starred) control.title = 'Unstar this experience';
        const icon = element('span', 'project-star__icon', experience.is_starred ? '\u2605' : '\u2606');
        icon.setAttribute('aria-hidden', 'true');
        control.append(
            icon,
            element('span', '', experience.is_starred ? 'Starred' : isAuthenticated ? 'Star' : 'Sign in to star'),
            element('span', 'project-star__count', String(experience.star_count)),
        );
        wrapper.append(control);
        return wrapper;
    }

    function experienceItem(experience) {
        const item = element('li', 'experience-item');
        item.dataset.experienceId = experience.id;
        const thumbnail = safeHttpUrl(experience.thumbnail);
        if (thumbnail) {
            const image = element('img', 'experience-thumbnail');
            image.src = thumbnail;
            image.alt = `Preview of ${experience.title}`;
            image.loading = 'lazy';
            image.width = 480;
            image.height = 270;
            item.append(image);
        }

        const heading = element('div', 'experience-item-heading');
        heading.append(
            element('h3', '', experience.title),
            element('span', 'experience-period', formatDate(experience.started_at) || 'Start date not specified'),
        );
        item.append(heading, element('p', 'experience-description', experience.description));
        item.append(element(
            'p', 'experience-status',
            experience.ended_at ? `finished ${formatDate(experience.ended_at)}` : 'on-going',
        ));

        const actions = element('div', 'experience-actions');
        actions.append(starControl(experience));
        if (grid.dataset.editUrlTemplate) {
            const edit = element('a', 'button button-secondary', 'Edit');
            edit.href = actionUrl(grid.dataset.editUrlTemplate, experience.id);
            edit.setAttribute('aria-label', `Edit ${experience.title}`);
            actions.append(edit);
        }
        if (isOwner) {
            const remove = element('button', 'button button-danger-outline', 'Delete');
            remove.type = 'button';
            remove.setAttribute('popovertarget', `delete-experience-${experience.id}`);
            remove.setAttribute('aria-label', `Delete ${experience.title}`);
            actions.append(remove);
        }
        item.append(actions);
        return item;
    }

    function deleteModal(experience) {
        const id = `delete-experience-${experience.id}`;
        const titleId = `delete-experience-title-${experience.id}`;
        const descriptionId = `delete-experience-description-${experience.id}`;
        const modal = element('div', 'project-delete-modal');
        modal.id = id;
        modal.setAttribute('popover', 'auto');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', titleId);
        modal.setAttribute('aria-describedby', descriptionId);

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
        const heading = element('h2', '', 'Let this chapter go?');
        heading.id = titleId;
        const question = element('p');
        question.id = descriptionId;
        question.append('Are you sure you want to delete ', element('strong', '', experience.title), '? This action cannot be undone.');
        const actions = element('div', 'project-delete-modal__actions');
        const keep = element('button', 'button button-secondary', 'Cancel');
        keep.type = 'button';
        keep.setAttribute('popovertarget', id);
        keep.setAttribute('popovertargetaction', 'hide');
        const form = element('form');
        form.method = 'post';
        form.action = actionUrl(grid.dataset.detailUrlTemplate, experience.id);
        form.append(element('button', 'button button-danger', 'Yes, Delete'));
        form.querySelector('button').type = 'submit';
        actions.append(keep, form);
        content.append(close, element('p', 'eyebrow', 'Delete experience'), heading, question, actions);
        modal.append(backdrop, content);
        return modal;
    }

    function showEmpty(query, count) {
        empty.hidden = count !== 0;
        emptyTitle.textContent = query ? 'No matching experiences found.' : 'No experiences have been added yet.';
        emptyMessage.textContent = query
            ? `We couldn't find an experience titled \u201C${query}\u201D.`
            : 'Belum ada pengalaman yang ditambahkan.';
        if (emptyAdd) emptyAdd.hidden = Boolean(query);
    }

    function renderExperiences(query) {
        for (const list of categoryLists) {
            const items = experiences.filter(experience => experience.category === list.dataset.experienceCategory);
            if (items.length) {
                list.replaceChildren(...items.map(experienceItem));
            } else {
                list.replaceChildren(element(
                    'li', 'experience-category-empty',
                    query ? 'No matching entries in this category.' : 'No entries in this category yet.',
                ));
            }
        }
        if (isOwner) deleteModals.replaceChildren(...experiences.map(deleteModal));
        showEmpty(query, experiences.length);
    }

    async function loadExperiences(query = '') {
        const currentRequest = ++requestNumber;
        if (listController) listController.abort();
        listController = new AbortController();
        loading.hidden = false;
        error.hidden = true;
        clearLink.hidden = !query;

        try {
            const url = new URL(grid.dataset.apiUrl, window.location.origin);
            if (query) url.searchParams.set('title', query);
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
                signal: listController.signal,
            });
            if (!response.ok) throw new Error(`Experiences request failed: ${response.status}`);
            const data = await response.json();
            if (!Array.isArray(data)) throw new Error('Unexpected experiences response');
            if (currentRequest !== requestNumber) return;
            experiences = data;
            hasApiData = true;
            renderExperiences(query);
        } catch (fetchError) {
            if (currentRequest !== requestNumber || fetchError.name === 'AbortError') return;
            console.error('Could not load experiences:', fetchError);
            error.hidden = false;
            showToast('Experiences could not load', 'Please try again. The last available entries are still shown.', 'error');
        } finally {
            if (currentRequest === requestNumber) {
                loading.hidden = true;
                listController = null;
            }
        }
    }

    function updateSearch(query) {
        const url = new URL(window.location.href);
        if (query) url.searchParams.set('title', query);
        else url.searchParams.delete('title');
        window.history.replaceState({}, '', url);
        loadExperiences(query);
    }

    searchForm.hidden = false;
    searchInput.value = new URLSearchParams(window.location.search).get('title') || '';
    searchForm.addEventListener('submit', event => {
        event.preventDefault();
        clearTimeout(searchTimeout);
        updateSearch(searchInput.value.trim());
    });
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => updateSearch(searchInput.value.trim()), 300);
    });
    clearLink.addEventListener('click', event => {
        event.preventDefault();
        clearTimeout(searchTimeout);
        searchInput.value = '';
        updateSearch('');
        searchInput.focus();
    });
    retryButton.addEventListener('click', () => loadExperiences(searchInput.value.trim()));
    window.addEventListener('popstate', () => {
        clearTimeout(searchTimeout);
        searchInput.value = new URLSearchParams(window.location.search).get('title') || '';
        loadExperiences(searchInput.value.trim());
    });

    grid.addEventListener('submit', async event => {
        const form = event.target.closest('form.project-star');
        if (!form) return;
        event.preventDefault();
        if (!isAuthenticated) {
            window.location.assign(loginUrl());
            return;
        }
        const item = form.closest('[data-experience-id]');
        if (!item) return;
        const button = form.querySelector('button[type="submit"]');
        button.disabled = true;
        try {
            const { response, result } = await mutation(
                actionUrl(grid.dataset.starUrlTemplate, item.dataset.experienceId), 'POST',
            );
            if (!response.ok) {
                showMutationError(response, result, 'Could not update the star. Please try again.');
                return;
            }
            form.replaceWith(starControl(result));
            const index = experiences.findIndex(experience => experience.id === result.id);
            if (index !== -1) experiences[index] = result;
            else if (!hasApiData) loadExperiences(searchInput.value.trim());
            showToast(result.is_starred ? 'Experience starred' : 'Star removed', result.title, 'success');
        } catch (fetchError) {
            showToast('Star update failed', 'Could not connect. Please try again.', 'error');
        } finally {
            button.disabled = false;
        }
    });

    deleteModals.addEventListener('submit', async event => {
        const form = event.target.closest('form');
        const modal = form?.closest('[id^="delete-experience-"]');
        if (!modal || !isOwner) return;
        event.preventDefault();
        const id = modal.id.slice('delete-experience-'.length);
        const button = form.querySelector('button[type="submit"]');
        button.disabled = true;
        try {
            const { response, result } = await mutation(
                actionUrl(grid.dataset.detailUrlTemplate, id), 'DELETE',
            );
            if (!response.ok) {
                showMutationError(response, result, 'Could not delete the experience. Please try again.');
                return;
            }
            const title = modal.querySelector('strong')?.textContent || 'Experience';
            if (modal.matches(':popover-open')) modal.hidePopover();
            if (hasApiData) {
                experiences = experiences.filter(experience => experience.id !== id);
                renderExperiences(searchInput.value.trim());
            } else {
                const item = [...grid.querySelectorAll('[data-experience-id]')]
                    .find(candidate => candidate.dataset.experienceId === id);
                const list = item?.closest('[data-experience-category]');
                item?.remove();
                if (list && !list.querySelector('.experience-item')) {
                    list.replaceChildren(element('li', 'experience-category-empty', 'No entries in this category yet.'));
                }
                modal.remove();
                showEmpty(searchInput.value.trim(), grid.querySelectorAll('.experience-item').length);
                loadExperiences(searchInput.value.trim());
            }
            showToast('Experience deleted', `"${title}" has been deleted.`, 'success');
        } catch (fetchError) {
            showToast('Delete failed', 'Could not connect. Please try again.', 'error');
        } finally {
            button.disabled = false;
        }
    });

    const createModal = document.getElementById('experience-create-modal');
    if (createModal) {
        const createForm = document.getElementById('experience-create-form');
        const createButton = document.getElementById('experience-create-submit');
        const generalError = document.getElementById('experience-create-error-general');
        const closeButtons = createModal.querySelectorAll('[data-close-experience-modal]');
        let submitting = false;
        let opener = null;

        function clearValidation() {
            createForm.querySelectorAll('[data-api-error]').forEach(node => node.remove());
            createForm.querySelectorAll('[aria-invalid]').forEach(field => {
                field.removeAttribute('aria-invalid');
                field.removeAttribute('aria-errormessage');
            });
            generalError.textContent = '';
            generalError.hidden = true;
        }

        function showValidation(result) {
            let firstInvalid = null;
            for (const [name, details] of Object.entries(result)) {
                const message = (Array.isArray(details) ? details : [details]).map(String).join(' ');
                const field = createForm.elements.namedItem(name);
                const group = field?.closest('.form-group');
                if (!group) {
                    generalError.textContent = message;
                    generalError.hidden = false;
                    continue;
                }
                const fieldError = element('p', 'form-error', message);
                fieldError.id = `experience-create-error-${name}`;
                fieldError.dataset.apiError = '';
                group.append(fieldError);
                field.setAttribute('aria-invalid', 'true');
                field.setAttribute('aria-errormessage', fieldError.id);
                if (!firstInvalid) firstInvalid = field;
            }
            firstInvalid?.focus();
        }

        function setSubmitting(value) {
            submitting = value;
            createButton.disabled = value;
            closeButtons.forEach(button => { button.disabled = value; });
            createForm.setAttribute('aria-busy', String(value));
        }

        [document.getElementById('experience-create-open'), emptyAdd].forEach(trigger => {
            if (!trigger) return;
            trigger.addEventListener('click', event => {
                if (typeof createModal.showModal !== 'function') return;
                event.preventDefault();
                opener = trigger;
                clearValidation();
                createModal.showModal();
                createForm.elements.namedItem('title').focus();
            });
        });
        closeButtons.forEach(button => button.addEventListener('click', () => {
            if (!submitting) createModal.close();
        }));
        createModal.addEventListener('cancel', event => {
            if (submitting) event.preventDefault();
        });
        createModal.addEventListener('close', () => {
            createForm.reset();
            clearValidation();
            opener?.focus();
        });

        createForm.addEventListener('submit', async event => {
            event.preventDefault();
            if (submitting) return;
            clearValidation();
            setSubmitting(true);
            const formData = new FormData(createForm);
            const payload = {
                title: String(formData.get('title') ?? ''),
                description: String(formData.get('description') ?? ''),
                category: String(formData.get('category') ?? ''),
                thumbnail: String(formData.get('thumbnail') ?? '').trim() || null,
                started_at: String(formData.get('started_at') ?? '') || null,
                ended_at: String(formData.get('ended_at') ?? '') || null,
            };
            try {
                const { response, result } = await mutation(createForm.action, 'POST', payload);
                if (response.status === 400 && result && typeof result === 'object') {
                    showValidation(result);
                    showToast('Check experience details', errorMessage(result, 'Please correct the highlighted fields.'), 'error');
                    return;
                }
                if (!response.ok) {
                    showMutationError(response, result, 'Could not add the experience. Please try again.');
                    return;
                }
                createModal.close();
                searchInput.value = '';
                updateSearch('');
                showToast('Experience added', `"${result.title}" has been added.`, 'success');
            } catch (fetchError) {
                showToast('Could not add experience', 'Could not connect. Please try again.', 'error');
            } finally {
                setSubmitting(false);
            }
        });
    }

    loadExperiences(searchInput.value.trim());
});

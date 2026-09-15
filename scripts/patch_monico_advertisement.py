from pathlib import Path

p = Path('monicoone.html')
s = p.read_text(encoding='utf-8')

# 1) Appwrite SDK
sdk = '<script src="https://cdn.jsdelivr.net/npm/appwrite@17.0.0"></script>'
if sdk not in s:
    marker = '<script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-database-compat.js"></script>'
    if marker not in s:
        raise SystemExit('Firebase SDK marker not found')
    s = s.replace(marker, marker + '\n    ' + sdk, 1)

# 2) Advertisement CSS
css_marker = '</style>'
ad_css = r'''
        /* Advertisement slots */
        .ad-slot { width: 100%; min-height: 0; margin-top: 10px; }
        .ad-slot:empty { display: none; }
        .ad-card { width: 100%; overflow: hidden; border-radius: 18px; border: 1px solid rgba(148,163,184,.28); background: rgba(255,255,255,.92); box-shadow: 0 4px 18px rgba(15,23,42,.08); }
        .dark .ad-card { background: rgba(30,41,59,.9); border-color: rgba(71,85,105,.5); }
        .ad-card img, .ad-card video { display:block; width:100%; max-height:420px; object-fit:contain; }
        .ad-card iframe { display:block; width:100%; min-height:180px; border:0; }
        .ad-label { padding:5px 10px; font-size:9px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.06em; }
        .ad-empty { display:none; }
'''
if '/* Advertisement slots */' not in s:
    s = s.replace(css_marker, ad_css + '\n    ' + css_marker, 1)

# 3) Six placement slots. Each slot is directly beneath its section.
placements = {
    'grid1Section': '<div id="adSlotAdvertising" class="ad-slot" data-ad-placement="advertising"></div>',
    'grid2Section': '<div id="adSlotFlatBonus" class="ad-slot" data-ad-placement="flat_bonus"></div>',
    'grid3Section': '<div id="adSlotHeadOffice" class="ad-slot" data-ad-placement="head_office_circular"></div>',
    'grid4Section': '<div id="adSlotSalaryTA" class="ad-slot" data-ad-placement="salary_ta_bill"></div>',
    'grid5Section': '<div id="adSlotSalesReport" class="ad-slot" data-ad-placement="sales_report"></div>',
    'productLaunchSection': '<div id="adSlotNewProduct" class="ad-slot" data-ad-placement="new_product_launched"></div>',
}
for section_id, slot in placements.items():
    if slot not in s:
        needle = f'</div>\n\n                    <!-- ' if False else None
        # Find the section closing by locating its opening tag, then the next known sibling comment.
        start = s.find(f'<div id="{section_id}"')
        if start < 0:
            raise SystemExit(f'{section_id} not found')
        if section_id == 'grid1Section':
            end_marker = '                    <!-- Grid 2 to 5: Horizontal Scroll -->'
        elif section_id == 'grid2Section':
            end_marker = '                    <div id="grid3Section"'
        elif section_id == 'grid3Section':
            end_marker = '                    <div id="grid4Section"'
        elif section_id == 'grid4Section':
            end_marker = '                    <div id="grid5Section"'
        elif section_id == 'grid5Section':
            end_marker = '                    <!-- Product Training Section -->'
        else:
            end_marker = '                    <!-- Product Wise Target Sheet Section -->'
        end = s.find(end_marker, start)
        if end < 0:
            raise SystemExit(f'end marker for {section_id} not found')
        s = s[:end] + '\n\n                    ' + slot + '\n' + s[end:]

# 4) Admin Advertisement tab button.
button_marker = '<button onclick="switchAdminTab(\'user\')" id="tabBtnUser"'
if 'id="tabBtnAdvertisement"' not in s:
    pos = s.find(button_marker)
    if pos < 0:
        raise SystemExit('Admin user tab button not found')
    button_line_end = s.find('</button>', pos)
    if button_line_end < 0:
        raise SystemExit('Admin user tab button end not found')
    button_line_end += len('</button>')
    ad_button = '\n                <button onclick="switchAdminTab(\'advertisement\')" id="tabBtnAdvertisement" class="py-2.5 rounded-lg text-slate-600 dark:text-slate-400 transition">Advertisement</button>'
    s = s[:button_line_end] + ad_button + s[button_line_end:]

# 5) Admin Advertisement tab content, inserted before USER TAB.
if 'id="tabContentAdvertisement"' not in s:
    user_tab = '                <!-- USER TAB -->'
    pos = s.find(user_tab)
    if pos < 0:
        raise SystemExit('USER TAB marker not found')
    ad_tab = r'''                <!-- ADVERTISEMENT TAB -->
                <div id="tabContentAdvertisement" class="space-y-4 hidden pb-8">
                    <div class="rounded-2xl border border-primary/20 bg-primary/5 p-4 space-y-3">
                        <div class="flex items-center justify-between gap-2">
                            <h5 id="advertisementFormTitle" class="text-sm font-bold text-primary">নতুন Advertisement</h5>
                            <span class="text-[9px] font-bold text-slate-500">Appwrite Database</span>
                        </div>
                        <input type="hidden" id="editAdvertisementKey" value="">
                        <input type="text" id="advertisementTitleInput" placeholder="Advertisement Title (ঐচ্ছিক)" class="w-full px-3 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs outline-none">
                        <select id="advertisementPlacementInput" class="w-full px-3 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold outline-none">
                            <option value="advertising">Advertising</option>
                            <option value="flat_bonus">Flat Bonus Sheet</option>
                            <option value="head_office_circular">Head Office Circular</option>
                            <option value="salary_ta_bill">Salary TA Bill</option>
                            <option value="sales_report">Sales Report</option>
                            <option value="new_product_launched">New Product Launched</option>
                        </select>
                        <textarea id="advertisementCodeInput" placeholder="Advertisement Code / HTML এখানে দিন...\nউদাহরণ: <a href=&quot;...&quot;><img src=&quot;...&quot;></a>" rows="7" class="w-full px-3 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono outline-none resize-y"></textarea>
                        <div class="flex gap-2">
                            <button onclick="saveAdvertisementItem()" id="advertisementSaveBtn" class="flex-1 py-2.5 bg-primary text-white font-bold rounded-xl text-xs shadow-xs flex items-center justify-center gap-1.5"><i class="fa-solid fa-bullhorn"></i><span id="advertisementSaveBtnText">Advertisement Save</span></button>
                            <button onclick="resetAdvertisementForm()" id="advertisementCancelBtn" class="hidden px-4 py-2.5 bg-slate-200 dark:bg-slate-700 text-xs font-bold rounded-xl">বাতিল</button>
                        </div>
                        <p class="text-[9px] text-slate-500 dark:text-slate-400">প্রতি Placement-এ একবারে সর্বোচ্চ ১টি Advertisement থাকবে। নতুনটি Save করলে ঐ Placement-এর পুরোনো Advertisement replace হবে।</p>
                    </div>
                    <div>
                        <div class="relative mb-2">
                            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><i class="fa-solid fa-magnifying-glass text-xs"></i></span>
                            <input type="text" id="adminSearchAdvertisement" oninput="filterAdminAdvertisements(this.value)" placeholder="Advertisement খুঁজুন..." class="w-full pl-9 pr-4 py-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs focus:ring-2 focus:ring-primary outline-none shadow-xs">
                        </div>
                        <div id="adminAdvertisementList" class="space-y-2"></div>
                    </div>
                </div>

'''
    s = s[:pos] + ad_tab + s[pos:]

# 6) Appwrite Advertisement logic. It is isolated from Firebase so existing modules remain unchanged.
if '/* MONICO ADVERTISEMENT - APPWRITE */' not in s:
    marker = '        const firebaseConfig = {'
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit('firebaseConfig marker not found')
    ad_js = r'''        /* MONICO ADVERTISEMENT - APPWRITE */
        const { Client: AppwriteClient, Databases: AppwriteDatabases, ID: AppwriteID, Query: AppwriteQuery } = Appwrite;
        const appwriteClient = new AppwriteClient();
        appwriteClient.setEndpoint('https://cloud.appwrite.io/v1').setProject('6aa0d2b3002010d6ab15');
        const appwriteDatabases = new AppwriteDatabases(appwriteClient);
        const APPWRITE_DB_ID = '6aa0d2d500227db84fa2';
        const APPWRITE_AD_COLLECTION_ID = '6aa3bcf400025aaa3d22';
        const AD_PLACEMENTS = {
            advertising: { label: 'Advertising', slot: 'adSlotAdvertising' },
            flat_bonus: { label: 'Flat Bonus Sheet', slot: 'adSlotFlatBonus' },
            head_office_circular: { label: 'Head Office Circular', slot: 'adSlotHeadOffice' },
            salary_ta_bill: { label: 'Salary TA Bill', slot: 'adSlotSalaryTA' },
            sales_report: { label: 'Sales Report', slot: 'adSlotSalesReport' },
            new_product_launched: { label: 'New Product Launched', slot: 'adSlotNewProduct' }
        };
        let globalAppwriteAdvertisements = [];
        let appwriteAdSubscription = null;

        function adDocCode(doc) { return String(doc.code ?? doc.adCode ?? doc.html ?? doc.content ?? doc.advertisementCode ?? ''); }
        function adDocPlacement(doc) { return String(doc.placement ?? doc.position ?? doc.place ?? 'advertising'); }
        function adDocTitle(doc) { return String(doc.title ?? doc.name ?? 'Advertisement'); }
        function adSafeHtml(code) {
            const wrap = document.createElement('div');
            wrap.innerHTML = code || '';
            wrap.querySelectorAll('script').forEach(x => x.remove());
            wrap.querySelectorAll('iframe').forEach(x => {
                x.setAttribute('loading', 'lazy');
                x.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
            });
            return wrap.innerHTML;
        }
        function renderAdvertisementPlacement(placement) {
            const info = AD_PLACEMENTS[placement];
            if (!info) return;
            const slot = document.getElementById(info.slot);
            if (!slot) return;
            const ad = globalAppwriteAdvertisements.find(x => adDocPlacement(x) === placement);
            if (!ad) { slot.innerHTML = ''; slot.classList.add('ad-empty'); return; }
            const code = adDocCode(ad);
            if (!code.trim()) { slot.innerHTML = ''; slot.classList.add('ad-empty'); return; }
            slot.classList.remove('ad-empty');
            slot.innerHTML = `<div class="ad-card"><div class="ad-label">Advertisement</div><div class="ad-content">${adSafeHtml(code)}</div></div>`;
        }
        function renderAllAdvertisements() { Object.keys(AD_PLACEMENTS).forEach(renderAdvertisementPlacement); }
        function refreshAdvertisementAdminList() {
            filterAdminAdvertisements(document.getElementById('adminSearchAdvertisement')?.value || '');
        }
        async function loadAdvertisements() {
            try {
                const result = await appwriteDatabases.listDocuments(APPWRITE_DB_ID, APPWRITE_AD_COLLECTION_ID, [AppwriteQuery.limit(100)]);
                globalAppwriteAdvertisements = result.documents || [];
                renderAllAdvertisements();
                refreshAdvertisementAdminList();
            } catch (error) {
                console.error('Appwrite Advertisement load error:', error);
                // Keep existing Firebase app working even when Advertisement permissions/schema are not ready.
                Object.keys(AD_PLACEMENTS).forEach(p => renderAdvertisementPlacement(p));
            }
        }
        function subscribeAdvertisements() {
            try {
                if (appwriteAdSubscription) appwriteAdSubscription();
                appwriteAdSubscription = appwriteClient.subscribe(`databases.${APPWRITE_DB_ID}.collections.${APPWRITE_AD_COLLECTION_ID}.documents`, () => loadAdvertisements());
            } catch (error) { console.warn('Appwrite Realtime subscription unavailable:', error); }
        }
        function adDataCandidates(code, placement, title) {
            const base = { placement };
            if (title) base.title = title;
            return [
                { ...base, code },
                { ...base, adCode: code },
                { ...base, html: code },
                { ...base, content: code },
                { ...base, advertisementCode: code }
            ];
        }
        async function createAdvertisementFlexible(code, placement, title) {
            let lastError = null;
            for (const data of adDataCandidates(code, placement, title)) {
                try { return await appwriteDatabases.createDocument(APPWRITE_DB_ID, APPWRITE_AD_COLLECTION_ID, AppwriteID.unique(), data); }
                catch (e) { lastError = e; }
            }
            throw lastError || new Error('Advertisement create failed');
        }
        async function updateAdvertisementFlexible(id, code, placement, title) {
            let lastError = null;
            for (const data of adDataCandidates(code, placement, title)) {
                try { return await appwriteDatabases.updateDocument(APPWRITE_DB_ID, APPWRITE_AD_COLLECTION_ID, id, data); }
                catch (e) { lastError = e; }
            }
            throw lastError || new Error('Advertisement update failed');
        }
        async function deleteAdvertisementDocument(id) {
            return appwriteDatabases.deleteDocument(APPWRITE_DB_ID, APPWRITE_AD_COLLECTION_ID, id);
        }
        async function replaceAdvertisementForPlacement(placement, code, title, editId) {
            const current = globalAppwriteAdvertisements.filter(x => adDocPlacement(x) === placement);
            if (editId) {
                await updateAdvertisementFlexible(editId, code, placement, title);
                for (const old of current) if (old.$id !== editId) await deleteAdvertisementDocument(old.$id);
            } else {
                for (const old of current) await deleteAdvertisementDocument(old.$id);
                await createAdvertisementFlexible(code, placement, title);
            }
        }
        window.saveAdvertisementItem = async function() {
            const editId = document.getElementById('editAdvertisementKey').value.trim();
            const title = document.getElementById('advertisementTitleInput').value.trim();
            const placement = document.getElementById('advertisementPlacementInput').value;
            const code = document.getElementById('advertisementCodeInput').value.trim();
            const btn = document.getElementById('advertisementSaveBtn');
            if (!placement || !code) { showToast('Placement এবং Advertisement Code দিন'); return; }
            btn.disabled = true;
            try {
                await replaceAdvertisementForPlacement(placement, code, title, editId);
                showToast('Advertisement সফলভাবে সংরক্ষণ হয়েছে!');
                resetAdvertisementForm();
                await loadAdvertisements();
            } catch (error) {
                console.error('Advertisement save error:', error);
                showToast('Advertisement Save হয়নি। Appwrite Collection permissions/attributes চেক করুন।');
            } finally { btn.disabled = false; }
        };
        window.editAdvertisementItem = function(id) {
            const ad = globalAppwriteAdvertisements.find(x => x.$id === id);
            if (!ad) return;
            document.getElementById('editAdvertisementKey').value = id;
            document.getElementById('advertisementTitleInput').value = adDocTitle(ad);
            document.getElementById('advertisementPlacementInput').value = adDocPlacement(ad);
            document.getElementById('advertisementCodeInput').value = adDocCode(ad);
            document.getElementById('advertisementFormTitle').innerText = 'Advertisement Edit করুন';
            document.getElementById('advertisementSaveBtnText').innerText = 'Update করুন';
            document.getElementById('advertisementCancelBtn').classList.remove('hidden');
        };
        window.deleteAdvertisementItem = async function(id) {
            if (!confirm('Advertisementটি ডিলিট করতে চান?')) return;
            try { await deleteAdvertisementDocument(id); showToast('Advertisement ডিলিট হয়েছে!'); await loadAdvertisements(); }
            catch (error) { console.error(error); showToast('Advertisement ডিলিট করা যায়নি!'); }
        };
        window.resetAdvertisementForm = function() {
            document.getElementById('editAdvertisementKey').value = '';
            document.getElementById('advertisementTitleInput').value = '';
            document.getElementById('advertisementPlacementInput').value = 'advertising';
            document.getElementById('advertisementCodeInput').value = '';
            document.getElementById('advertisementFormTitle').innerText = 'নতুন Advertisement';
            document.getElementById('advertisementSaveBtnText').innerText = 'Advertisement Save';
            document.getElementById('advertisementCancelBtn').classList.add('hidden');
        };
        window.filterAdminAdvertisements = function(keyword) {
            const list = document.getElementById('adminAdvertisementList');
            if (!list) return;
            const k = (keyword || '').toLowerCase().trim();
            list.innerHTML = '';
            globalAppwriteAdvertisements.forEach(ad => {
                const placement = adDocPlacement(ad);
                const label = AD_PLACEMENTS[placement]?.label || placement;
                const title = adDocTitle(ad);
                const code = adDocCode(ad);
                const hay = `${title} ${label} ${code}`.toLowerCase();
                if (k && !hay.includes(k)) return;
                list.innerHTML += `<div class="flex items-center justify-between gap-2 p-2.5 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 text-xs"><div class="truncate max-w-[65%]"><span class="font-bold block truncate">${title}</span><span class="text-[9px] text-primary block">${label}</span><span class="text-[9px] text-slate-400 block truncate">${code.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span></div><div class="flex items-center space-x-1.5 shrink-0"><button onclick="editAdvertisementItem('${ad.$id}')" class="p-1 text-primary hover:bg-primary/10 rounded" title="এডিট"><i class="fa-solid fa-pen-to-square"></i></button><button onclick="deleteAdvertisementItem('${ad.$id}')" class="p-1 text-danger hover:bg-danger/10 rounded" title="ডিলিট"><i class="fa-solid fa-trash"></i></button></div></div>`;
            });
            if (!list.innerHTML) list.innerHTML = '<p class="text-xs text-slate-400 text-center py-4">কোনো Advertisement পাওয়া যায়নি।</p>';
        };
        function initAdvertisementModule() { loadAdvertisements(); subscribeAdvertisements(); }

'''
    s = s[:pos] + ad_js + s[pos:]

# 7) Initialize advertisement module after dashboard listener setup.
needle = '            initListeners(); // Initialize listeners with cache support\n'
if '            initAdvertisementModule();\n' not in s:
    if needle not in s:
        raise SystemExit('activateDashboard listener marker not found')
    s = s.replace(needle, needle + '            initAdvertisementModule();\n', 1)

# 8) Admin panel loads Advertisement list.
needle = '            renderAdminUsers();\n'
if '            loadAdvertisements();\n' not in s[s.find('window.openAdminPanel'):s.find('window.openAdminPanel')+2500]:
    pos = s.find(needle, s.find('window.openAdminPanel'))
    if pos < 0:
        raise SystemExit('openAdminPanel user render marker not found')
    s = s[:pos] + needle + '            loadAdvertisements();\n' + s[pos+len(needle):]

# 9) Add advertisement to switchAdminTab list.
old = "['slider', 'menu', 'sidebarMenu', 'notice', 'popup', 'productCard', 'trainingCard', 'targetSheet', 'user']"
new = "['slider', 'menu', 'sidebarMenu', 'notice', 'popup', 'productCard', 'trainingCard', 'targetSheet', 'advertisement', 'user']"
if old in s:
    s = s.replace(old, new, 1)

# 10) Expand admin tab grid from 9 columns to 10.
s = s.replace('grid grid-cols-3 md:grid-cols-9 gap-2 bg-slate-100', 'grid grid-cols-3 md:grid-cols-10 gap-2 bg-slate-100', 1)

p.write_text(s, encoding='utf-8')
print('Advertisement patch applied successfully')

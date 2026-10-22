const chatBox = document.getElementById('chat-box');
const inputBox = document.getElementById('message-input');
const watchlist = document.getElementById('watchlist');
const historyList = document.getElementById('chat-history');
const welcome = document.getElementById('welcome');
const sendButton = document.getElementById('send-button');
const STORAGE_KEYS = { watchlist: 'finsight.watchlist.v1', history: 'finsight.history.v1' };
let activeChatId = null;
let chats = readStorage(STORAGE_KEYS.history, []);
let tracked = readStorage(STORAGE_KEYS.watchlist, []);

function readStorage(key, fallback) {
  try { const value = JSON.parse(sessionStorage.getItem(key)); return Array.isArray(value) ? value : fallback; }
  catch { return fallback; }
}
function saveState() {
  sessionStorage.setItem(STORAGE_KEYS.history, JSON.stringify(chats));
  sessionStorage.setItem(STORAGE_KEYS.watchlist, JSON.stringify(tracked));
}
function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}
function initials(value) {
  return String(value || '').split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase() || '•';
}
function renderWatchlist() {
  watchlist.replaceChildren();
  document.getElementById('watch-count').textContent = tracked.length;
  document.getElementById('watch-empty').hidden = tracked.length > 0;
  tracked.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = `<button class="watch-item" type="button" data-ticker="${escapeHTML(item.ticker)}"><span class="ticker-mark">${escapeHTML(initials(item.ticker))}</span><span class="watch-name"><strong>${escapeHTML(item.ticker)}</strong><small>${escapeHTML(item.company || 'Tracked company')}</small></span><svg class="sparkline" viewBox="0 0 38 20" fill="none" aria-hidden="true"><path d="M1 15.5 7 12l5 2.5 6-8 5 5 5-4 4 2 5-6" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></button>`;
    li.querySelector('button').addEventListener('click', () => sendMessage(`Analyze ${item.ticker}`));
    watchlist.appendChild(li);
  });
}
function renderHistory() {
  historyList.replaceChildren();
  document.getElementById('history-empty').hidden = chats.length > 0;
  chats.forEach(chat => {
    const li = document.createElement('li');
    li.innerHTML = `<button class="history-item${chat.id === activeChatId ? ' active' : ''}" type="button"><span class="history-icon">▤</span><span>${escapeHTML(chat.title)}</span></button>`;
    li.querySelector('button').addEventListener('click', () => openChat(chat.id));
    historyList.appendChild(li);
  });
}
function makeMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  if (role === 'user') {
    wrapper.innerHTML = `<div class="message-content">${escapeHTML(text)}</div>`;
  } else {
    wrapper.innerHTML = `<div class="avatar message-avatar">FS</div><div class="message-content"><div class="message-label">FINSIGHT ANALYST</div><div class="message-text">${escapeHTML(text)}</div></div>`;
  }
  return wrapper;
}
function addUserMessage(text) { chatBox.appendChild(makeMessage('user', text)); scrollToBottom(); }
function addBotMessage(text) { const row = makeMessage('bot', text); chatBox.appendChild(row); scrollToBottom(); return row; }
function addLoading() {
  const row = document.createElement('div'); row.className = 'message bot'; row.id = 'loading';
  row.innerHTML = '<div class="avatar message-avatar">FS</div><div class="message-content"><div class="message-label">FINSIGHT ANALYST</div><div class="thinking"><span>Reviewing company data</span><span class="thinking-dots"><i></i><i></i><i></i></span></div></div>';
  chatBox.appendChild(row); scrollToBottom(); return row;
}
function renderInsight(insight, reply) {
  const row = document.createElement('div'); row.className = 'message bot';
  const tone = ['positive', 'negative'].includes(insight.sentiment_tone) ? insight.sentiment_tone : '';
  const risks = Array.isArray(insight.risk_factors) ? insight.risk_factors : [];
  const confidence = insight.confidence != null && Number.isFinite(Number(insight.confidence))
    ? `${escapeHTML(insight.confidence)}% confidence` : 'Data-derived signal';
  row.innerHTML = `<div class="avatar message-avatar">FS</div><div class="message-content"><div class="message-label">FINSIGHT ANALYST</div><div class="message-text">${escapeHTML(reply || '')}</div><article class="insight-card"><div class="insight-head"><div class="company-identity"><span class="company-monogram">${escapeHTML(initials(insight.ticker))}</span><div><h3>${escapeHTML(insight.company)} <span style="color:#909caf;font-weight:500">${escapeHTML(insight.ticker)}</span></h3><p>Latest available company snapshot</p></div></div><span class="sentiment-pill ${tone}">${escapeHTML(insight.sentiment)}</span></div><div class="insight-grid"><div class="insight-row"><div class="insight-label">Revenue</div><div class="insight-value">${escapeHTML(insight.revenue?.value || 'Unavailable')} <span style="color:#8c98aa;font-weight:500">· ${escapeHTML(insight.revenue?.qoq || 'Growth unavailable')}</span></div></div><div class="insight-row"><div class="insight-label">Outlook</div><div class="insight-value outlook-tag">${escapeHTML(insight.outlook || 'Unavailable')}</div></div><div class="insight-row"><div class="insight-label">Key risk factors</div><div class="risk-tags">${risks.map(risk => `<span class="risk-tag">${escapeHTML(risk)}</span>`).join('') || '<span class="insight-value">Unavailable</span>'}</div></div><div class="insight-row"><div class="insight-label">Signal confidence</div><div class="insight-value">${confidence}</div></div></div><div class="insight-footer"><span class="data-note">Based on available market and financial data</span><button type="button" class="add-watch">＋ Add to watchlist</button></div></article></div>`;
  row.querySelector('.add-watch').addEventListener('click', event => {
    addToWatchlist(insight.ticker, insight.company);
    event.currentTarget.textContent = '✓ Added'; event.currentTarget.classList.add('added');
  });
  chatBox.appendChild(row); scrollToBottom(); return row;
}
function addToWatchlist(ticker, company) {
  const normalized = String(ticker || '').toUpperCase();
  if (!normalized || tracked.some(item => item.ticker === normalized)) return;
  tracked.unshift({ ticker: normalized, company: company || normalized });
  saveState(); renderWatchlist();
}
function titleForQuery(text) {
  return text.length > 28 ? `${text.slice(0, 27).trim()}…` : text;
}
function beginChat(query) {
  const chat = { id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}`, title: titleForQuery(query), messages: [] };
  chats.unshift(chat); chats = chats.slice(0, 30); activeChatId = chat.id; saveState(); renderHistory(); return chat;
}
function openChat(id) {
  const chat = chats.find(item => item.id === id); if (!chat) return;
  activeChatId = id; chatBox.replaceChildren();
  chat.messages.forEach(message => {
    if (message.type === 'insight') renderInsight(message.data, message.reply);
    else if (message.type === 'reply') addBotMessage(message.reply);
    else if (message.role === 'user') addUserMessage(message.text);
    else addBotMessage(message.text);
  });
  renderHistory();
}
async function sendMessage(override) {
  const message = String(override ?? inputBox.value).trim();
  if (!message || sendButton.disabled) return;
  if (welcome?.isConnected) welcome.remove();
  let chat = chats.find(item => item.id === activeChatId);
  if (!chat) chat = beginChat(message);
  addUserMessage(message); chat.messages.push({ role: 'user', text: message });
  if (chat.messages.length === 1) { chat.title = titleForQuery(message); renderHistory(); }
  inputBox.value = ''; inputBox.style.height = 'auto'; sendButton.disabled = true; addLoading();
  try {
    const history = chat.messages.slice(0, -1).map(item => {
      if (item.role === 'user') return { role: 'user', content: item.text };
      if (item.type === 'insight' || item.type === 'reply') return { role: 'assistant', content: item.reply };
      if (item.role === 'bot') return { role: 'assistant', content: item.text };
      return null;
    }).filter(Boolean);
    const response = await fetch('/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: message, history }) });
    const data = await response.json();
    document.getElementById('loading')?.remove();
    if (!response.ok || !data.success) throw new Error(data.error || 'The analysis could not be completed.');
    let answerRow;
    if (data.insight) {
      answerRow = renderInsight(data.insight, data.reply);
      chat.messages.push({ type: 'insight', data: data.insight, reply: data.reply });
    } else {
      answerRow = addBotMessage(data.reply);
      chat.messages.push({ type: 'reply', reply: data.reply });
    }
    saveState();
    if (data.needs_answer) {
      const recordIndex = chat.messages.length - 1;
      answerRow?.querySelector('.message-text')?.classList.add('answer-pending');
      requestDetailedAnswer(message, data.ticker, history, chat, recordIndex, answerRow, data.answer_type);
    }
  } catch (error) {
    document.getElementById('loading')?.remove();
    const messageText = error.message || 'Unable to retrieve financial information.';
    const row = makeMessage('bot', messageText); row.querySelector('.message-text').classList.add('error-message'); chatBox.appendChild(row);
    chat.messages.push({ role: 'bot', text: messageText }); saveState(); scrollToBottom();
  } finally { sendButton.disabled = false; inputBox.focus(); }
}
async function requestDetailedAnswer(query, ticker, history, chat, recordIndex, row, answerType) {
  try {
    const response = await fetch('/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, ticker, history })
    });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || 'Answer unavailable.');
    const message = chat.messages[recordIndex];
    if (message) {
      if (message.type === 'insight' || message.type === 'reply') message.reply = data.reply;
      saveState();
    }
    const text = row?.querySelector('.message-text');
    if (text?.isConnected) { text.textContent = data.reply; text.classList.remove('answer-pending'); }
  } catch (error) {
    const pendingText = row?.querySelector('.message-text');
    pendingText?.classList.remove('answer-pending');
    if (answerType === 'general_finance') {
      const fallback = 'I could not generate the detailed answer. Check the model configuration and try again.';
      const message = chat.messages[recordIndex];
      if (message?.type === 'reply') message.reply = fallback;
      saveState();
      const text = pendingText;
      if (text?.isConnected) { text.textContent = fallback; text.classList.remove('answer-pending'); }
    }
  }
}
function scrollToBottom() { chatBox.scrollTop = chatBox.scrollHeight; }

document.getElementById('message-form').addEventListener('submit', event => { event.preventDefault(); sendMessage(); });
inputBox.addEventListener('input', () => { inputBox.style.height = 'auto'; inputBox.style.height = `${Math.min(inputBox.scrollHeight, 130)}px`; });
inputBox.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); } });
document.querySelectorAll('.prompt-card').forEach(button => button.addEventListener('click', () => {
  const suffix = button.dataset.prompt.includes('earnings') ? 'Analyze earnings for ' : 'Analyze risks for ';
  inputBox.value = suffix; inputBox.focus(); inputBox.setSelectionRange(suffix.length, suffix.length);
}));
document.getElementById('new-chat').addEventListener('click', () => {
  activeChatId = null; chatBox.replaceChildren();
  const welcomeTemplate = document.createElement('div'); welcomeTemplate.className = 'welcome';
  welcomeTemplate.innerHTML = '<div class="welcome-icon"><span>✳</span></div><p class="eyebrow">YOUR PERSONAL FINANCIAL ANALYST</p><h1>Good research starts<br>with a <span>good question.</span></h1><p class="welcome-copy">Ask about any company, ticker, or finance topic. These prompts are just examples.</p><div class="prompt-grid"><button class="prompt-card" data-prompt="earnings"><span class="prompt-icon violet">↗</span><span><strong>Earnings overview</strong><small>Revenue, sentiment and key risks</small></span><span class="prompt-arrow">↗</span></button><button class="prompt-card" data-prompt="risk"><span class="prompt-icon amber">◈</span><span><strong>Explore risk factors</strong><small>Understand what could move a stock</small></span><span class="prompt-arrow">↗</span></button></div>';
  chatBox.appendChild(welcomeTemplate); welcomeTemplate.querySelectorAll('.prompt-card').forEach(button => button.addEventListener('click', () => { inputBox.value = button.dataset.prompt === 'earnings' ? 'Analyze earnings for ' : 'Analyze risks for '; inputBox.focus(); }));
  renderHistory(); inputBox.focus();
});
document.getElementById('clear-history').addEventListener('click', () => {
  chats = []; activeChatId = null; saveState(); renderHistory();
  document.getElementById('new-chat').click();
});
renderWatchlist(); renderHistory();

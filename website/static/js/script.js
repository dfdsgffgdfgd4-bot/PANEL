// Estado da aplicação
let appState = {
    keyVerified: false,
    currentKey: null,
    currentIP: null
};

// Elements
const loginSection = document.getElementById('login-section');
const downloadSection = document.getElementById('download-section');
const keyInput = document.getElementById('key');
const verifyBtn = document.getElementById('verify-btn');
const downloadBtn = document.getElementById('download-btn');
const registerIpBtn = document.getElementById('register-ip-btn');
const logoutBtn = document.getElementById('logout-btn');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');
const downloadMessage = document.getElementById('download-message');

// Obter IP do cliente
async function getClientIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        console.error('Erro ao obter IP:', error);
        return 'IP desconhecido';
    }
}

// Mostrar mensagem de erro
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    successMessage.classList.add('hidden');
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

// Mostrar mensagem de sucesso
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    setTimeout(() => {
        successMessage.classList.add('hidden');
    }, 5000);
}

// Mostrar mensagem de download
function showDownloadMessage(message, type = 'success') {
    downloadMessage.textContent = message;
    downloadMessage.className = `message ${type}`;
    downloadMessage.classList.remove('hidden');
    setTimeout(() => {
        downloadMessage.classList.add('hidden');
    }, 5000);
}

// Desabilitar botão
function disableButton(btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Processando...';
}

// Habilitar botão
function enableButton(btn, text) {
    btn.disabled = false;
    btn.innerHTML = text;
}

// Verificar key
verifyBtn.addEventListener('click', async () => {
    const key = keyInput.value.trim().toUpperCase();

    if (!key) {
        showError('Digite uma key válida!');
        return;
    }

    disableButton(verifyBtn);

    try {
        const response = await fetch('/api/check-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: key })
        });

        const data = await response.json();

        if (response.ok) {
            appState.keyVerified = true;
            appState.currentKey = key;
            
            // Atualizar informações
            document.getElementById('project-name').textContent = data.project;
            document.getElementById('role-name').textContent = data.role || 'N/A';
            document.getElementById('current-ip').textContent = appState.currentIP;

            // Obter status da key
            await updateKeyStatus();

            // Mostrar seção de download
            loginSection.classList.add('hidden');
            downloadSection.classList.remove('hidden');

            showSuccess(`Key verificada! Bem-vindo, ${data.role || 'Usuário'}!`);
        } else {
            showError(data.error || 'Erro ao verificar key');
        }
    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao conectar ao servidor');
    } finally {
        enableButton(verifyBtn, 'Verificar Key');
    }
});

// Atualizar status da key
async function updateKeyStatus() {
    try {
        const response = await fetch('/api/status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: appState.currentKey })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('ips-count').textContent = 
                `${data.ips_registrados}/${data.limite_ips}`;
        }
    } catch (error) {
        console.error('Erro ao obter status:', error);
    }
}

// Registrar IP
registerIpBtn.addEventListener('click', async () => {
    disableButton(registerIpBtn);

    try {
        const response = await fetch('/api/register-ip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: appState.currentKey })
        });

        const data = await response.json();

        if (response.ok) {
            showDownloadMessage('✅ IP registrado com sucesso!', 'success');
            await updateKeyStatus();
        } else {
            showDownloadMessage('❌ ' + (data.error || 'Erro ao registrar IP'), 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showDownloadMessage('❌ Erro ao conectar ao servidor', 'error');
    } finally {
        enableButton(registerIpBtn, '📝 Registrar IP');
    }
});

// Baixar script
downloadBtn.addEventListener('click', async () => {
    disableButton(downloadBtn);

    try {
        const response = await fetch('/api/download-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: appState.currentKey })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'irish_lagger.exe';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showDownloadMessage('✅ Script baixado com sucesso!', 'success');
        } else {
            const data = await response.json();
            showDownloadMessage('❌ ' + (data.error || 'Erro ao baixar script'), 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showDownloadMessage('❌ Erro ao conectar ao servidor', 'error');
    } finally {
        enableButton(downloadBtn, '⬇️ Baixar Script');
    }
});

// Logout
logoutBtn.addEventListener('click', () => {
    appState.keyVerified = false;
    appState.currentKey = null;
    keyInput.value = '';
    loginSection.classList.remove('hidden');
    downloadSection.classList.add('hidden');
    showSuccess('Desconectado com sucesso!');
});

// Inicializar
window.addEventListener('load', async () => {
    appState.currentIP = await getClientIP();
    console.log('IP do cliente:', appState.currentIP);
});

// Enter para enviar
keyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        verifyBtn.click();
    }
});

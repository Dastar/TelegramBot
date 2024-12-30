const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

class WhatsAppClient {
    constructor(id, exe) {
        this.client = new Client({
            authStrategy: new LocalAuth({clientId: id}),
            puppeteer: { 
                headless: true,
                executablePath: exe
             }
        });

        this.groups = new Map(); // Store groups with server 'g.us'
        this.targetGroup = null;
        this.reconnectAttempts = 0; // Track reconnection attempts
        this.maxReconnectAttempts = 5; // Limit retries to avoid loops
        this.ready = false;
        this.qr = false;
        this.initializeEvents();
    }

    initializeEvents() {
        // QR Code Event
        this.client.on('qr', (qr) => {
            console.log('[WhatsApp] QR event');
            this.qr = true;
            qrcode.generate(qr, { small: true });
        });

        // Ready Event
        this.client.on('ready', async () => {
            console.log('[WhatsApp] Client is ready!');
            this.ready = true;
            this.qr = false;
            this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
            // await this.cacheGroups(); // Cache groups on startup
        });

        // Disconnected Event
        this.client.on('disconnected', async (reason) => {
            console.log('[WhatsApp] Disconnected:', reason);
            this.qr = false;
            await this.reconnect(); // Attempt to reconnect
        });

        // Auth Failure Event
        this.client.on('auth_failure', (msg) => {
            this.qr = false;
            console.error('[WhatsApp] Authentication failure:', msg);
            console.log('[WhatsApp] Attempting re-authentication...');
            this.reconnect(); // Retry authentication
        });

        // Connection Lost Event
        this.client.on('change_state', (state) => {
            this.qr = false;
            console.log(`[WhatsApp] Connection state changed: ${state}`);
            if (state === 'CONFLICT' || state === 'UNLAUNCHED') {
                console.log('[WhatsApp] Attempting to force re-authentication...');
                this.client.initialize(); // Reinitialize the client
            }
        });

        // Catch Unexpected Errors
        this.client.on('error', (err) => {
            this.qr = false;
            console.error('[WhatsApp] Unexpected error:', err);
            console.log('[WhatsApp] Restarting client...');
            this.reconnect(); // Restart the client on error
        });
    }

    initialize() {
        console.log('[WhatsApp] Initializing client...');
        this.client.initialize();
    }

    async reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            console.log(`[WhatsApp] Reconnecting... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
            this.reconnectAttempts++;
            setTimeout(() => this.client.initialize(), 5000); // Retry after 5 seconds
        } else {
            console.error('[WhatsApp] Max reconnection attempts reached. Please restart the application.');
        }
    }

    async isLoggedIn() {
        try {
            const state = await this.client.getState();
            return state === 'CONNECTED';
        } catch {
            return false;
        }
    }

    isReady() {
        return this.ready;
    }

    isQrCode() {
        return this.qr;
    }

    async cacheGroups() {
        try {
            console.log('[WhatsApp] Getting chats');
            const allChats = await this.client.getChats();

            this.groups.clear(); // Clear existing cache
            allChats.forEach(chat => {
                if (chat.id.server === 'g.us') {
                    this.groups.set(chat.name, chat);
                }
            });

            console.log(`[WhatsApp] Cached ${this.groups.size} group(s) with '@g.us'.`);
            return this.groups.size
            
        } catch (err) {
            console.error(`[WhatsApp] Error caching groups: ${err}`);
            return -1;
        }
    }

    getTargetGroup(groupId) {
        const group = this.groups.get(groupId);
        if (group) {
            console.log(`[WhatsApp] Found target group: "${group.name}" (${group.id._serialized})`);
            return group;
        } else {
            console.log(`[WhatsApp] Could NOT find group with ID "${groupId}". Make sure this WhatsApp account is in that group!`);
            return null;
        }
    }

    async sendMessage(target, message) {
        if (!message) throw new Error('Message is empty');

        try {
            const result = await this.client.sendMessage(target.id._serialized, message);
            console.log('[WhatsApp] Message sent:', message);
            return result;
        } catch (err) {
            console.error('[WhatsApp] Error sending message:', err);
            throw err;
        }
    }

    async sendFiles(target, filePaths, caption = '') {
        if (!Array.isArray(filePaths)) {
            throw new Error('filePaths must be an array of file paths.');
        }
    
        const errors = []; // To store results for each file
        for (let i = 0; i < filePaths.length; i++) {
            const filePath = filePaths[i];
            if (!fs.existsSync(filePath)) {
                console.error(`[WhatsApp] File not found: ${filePath}`);
                errors.push(`File ${filePath} not found`);
                continue; // Skip this file and process the next one
            }
    
            try {
                // Load the file
                const media = await MessageMedia.fromFilePath(filePath);
                let result = null;
                if (i == filePaths.length - 1)
                {
                    result = await this.client.sendMessage(target.id._serialized, media, { caption });

                } else {
                    result = await this.client.sendMessage(target.id._serialized, media);
                }
                // Send the file with an optional caption
                console.log(`[WhatsApp] File sent: ${filePath}`);
            } catch (err) {
                console.error(`[WhatsApp] Error sending file (${filePath}):`, err);
                errors.push(err.message);
            }
        }
    
        if (errors.length == 0) return {success: true};
        else {
            const err = errors.join(' ');
            return {success: false, error: err};
        }
    }
    
}

module.exports = WhatsAppClient;

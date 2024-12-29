const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

class WhatsAppClient {
    constructor(id) {
        this.client = new Client({
            authStrategy: new LocalAuth({clientId: id}),
            puppeteer: { headless: true }
        });

        this.groups = new Map(); // Store groups with server 'g.us'
        this.targetGroup = null;
        this.reconnectAttempts = 0; // Track reconnection attempts
        this.maxReconnectAttempts = 5; // Limit retries to avoid loops

        this.initializeEvents();
    }

    initializeEvents() {
        // QR Code Event
        this.client.on('qr', (qr) => {
            console.log('[WhatsApp] QR event. Scan the code below:');
            qrcode.generate(qr, { small: true });
        });

        // Ready Event
        this.client.on('ready', async () => {
            console.log('[WhatsApp] Client is ready!');
            this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
            // await this.cacheGroups(); // Cache groups on startup
        });

        // Disconnected Event
        this.client.on('disconnected', async (reason) => {
            console.log('[WhatsApp] Disconnected:', reason);
            await this.reconnect(); // Attempt to reconnect
        });

        // Auth Failure Event
        this.client.on('auth_failure', (msg) => {
            console.error('[WhatsApp] Authentication failure:', msg);
            console.log('[WhatsApp] Attempting re-authentication...');
            this.reconnect(); // Retry authentication
        });

        // Connection Lost Event
        this.client.on('change_state', (state) => {
            console.log(`[WhatsApp] Connection state changed: ${state}`);
            if (state === 'CONFLICT' || state === 'UNLAUNCHED') {
                console.log('[WhatsApp] Attempting to force re-authentication...');
                this.client.initialize(); // Reinitialize the client
            }
        });

        // Catch Unexpected Errors
        this.client.on('error', (err) => {
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

    async cacheGroups() {
        try {
            console.log('[WhatsApp] Getting chats');
            const allChats = await this.client.getChats();

            this.groups.clear(); // Clear existing cache
            allChats.forEach(chat => {
                if (chat.id.server === 'g.us') {
                    this.groups.set(chat.id._serialized, chat);
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
}

module.exports = WhatsAppClient;

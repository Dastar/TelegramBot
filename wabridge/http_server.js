const express = require('express');
const bodyParser = require('body-parser');
const WhatsAppClient = require('./whatsappclient');

// Initialize Express app
const app = express();
const PORT = 3000;

const WANTED_GROUP_ID   = '120363386281984067@g.us';  

// Middleware
app.use(bodyParser.json());

// Initialize WhatsApp client
// const whatsapp = new WhatsAppClient();
// whatsapp.initialize();
let whatsapp = null;
app.post('/start', async (req, res) => {
    const clientId = req.body.clientId;
    console.log("Starting the client with id: ", clientId);
    if (whatsapp && whatsapp.initialized) {
        return res.json({ success: true, message: 'WhatsApp Client already initialized!' });
    }

    try {
        whatsapp = new WhatsAppClient(clientId);
        await whatsapp.initialize();
        res.json({ success: true, message: 'WhatsApp Client initialization started!' });
    } catch (err) {
        console.error('[Server] Error initializing WhatsApp Client:', err);
        res.status(500).json({ error: 'Failed to initialize WhatsApp Client.' });
    }
});

app.post('/cache', async(req, res) => {
    console.log("Caching groups")
        const val = await whatsapp.cacheGroups();
        res.json({size: val});

});

app.post('/is-connected', async(req, res) =>{
    const state = await whatsapp.isLoggedIn();
    res.json({message: `${state}`})
});

// API endpoint to send a message
app.post('/send-message', async (req, res) => {
    const { groupId, message } = req.body;

    if (!groupId || !message) {
        return res.status(400).json({ error: 'groupId and message are required.' });
    }

    try {
        const targetGroup = whatsapp.getTargetGroup(groupId);
        if (!targetGroup) {
            return res.status(404).json({ error: 'Group not found.' });
        }

        const result = await whatsapp.sendMessage(targetGroup, message);
        res.json({ success: true, result });
    } catch (err) {
        console.error('[HTTP Server] Error:', err);
        res.status(500).json({ error: 'Failed to send message.' });
    }
});

// API endpoint to list cached groups
app.get('/list-groups', (req, res) => {
    try {
        const groups = Array.from(whatsapp.groups.values()).map(group => ({
            id: group.id._serialized,
            name: group.name
        }));
        res.json({ success: true, groups });
    } catch (err) {
        console.error('[HTTP Server] Error fetching groups:', err);
        res.status(500).json({ error: 'Failed to fetch groups.' });
    }
});

app.post('/send-media', async (req, res) => {
    const { groupId, caption, links } = req.body;

    if (!groupId || !Array.isArray(links) || links.length === 0) {
        return res.status(400).json({ error: 'Group ID and a non-empty list of media links are required.' });
    }

    try {
        for (const link of links) {
            const media = await MessageMedia.fromUrl(link);
            await whatsappClient.sendMessage(groupId, media, caption);
            console.log(`[WhatsApp] Media sent from link: ${link}`);
        }
        res.json({ success: true, message: 'Media links sent successfully!' });
    } catch (err) {
        console.error('[WhatsApp] Error sending media links:', err);
        res.status(500).json({ error: 'Failed to send media links.' });
    }
});


// Start the HTTP server
app.listen(PORT, () => {
    console.log(`[Server] Listening on http://localhost:${PORT}`);
});

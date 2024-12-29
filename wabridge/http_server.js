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
    let state = await whatsapp.isLoggedIn();
    state = state && whatsapp.isReady();
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
    try {
        // Check if files were uploaded
        if (!req.body.media) {
            return res.status(400).json({ success: false, error: 'No files uploaded.' });
        }

        // Check group ID
        const groupId = req.body.groupId;
        if (!groupId) {
            return res.status(400).json({ success: false, error: 'No group ID provided.' });
        }

        const files = Array.isArray(req.body.media) ? req.body.media : [req.body.media]; // Handle single/multiple files
        const targetGroup = whatsapp.getTargetGroup(groupId);
        const result = await whatsapp.sendFiles(targetGroup, files, req.body.caption);
        console.log(result);

        if (result.success === true) {

        console.log("Sent files to wa");
            
            res.json({success: true});
        } else {
        console.log("failed to send files to wa");

            res.json({success: false, error: result.error});
        }
    } catch (err) {
        console.error('Error handling file upload:', err);
        res.status(500).json({ success: false, error: err.message });
    }
});


// Start the HTTP server
app.listen(PORT, () => {
    console.log(`[Server] Listening on http://localhost:${PORT}`);
});

<?php
// Configuration
$API_KEY = getenv('API_KEY');
$API_BASE_URL = 'http://localhost:5000/api';

// Function to make API requests
function makeApiRequest($endpoint) {
    global $API_KEY, $API_BASE_URL;
    
    $ch = curl_init($API_BASE_URL . $endpoint);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'X-API-Key: ' . $API_KEY,
        'Accept: application/json'
    ]);
    
    $response = curl_exec($ch);
    $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($statusCode === 200) {
        return json_decode($response, true);
    }
    return null;
}

// Fetch time entries
$timeEntries = makeApiRequest('/time-entries');
$projects = makeApiRequest('/projects');
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Time Entries (PHP View)</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Time Entries (PHP Integration)</h1>
        
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Available Projects</h5>
            </div>
            <div class="card-body">
                <ul class="list-group">
                    <?php foreach ($projects as $project): ?>
                        <li class="list-group-item"><?php echo htmlspecialchars($project); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0">Time Entries</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Project</th>
                                <th>Hours</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($timeEntries as $entry): ?>
                                <tr>
                                    <td><?php echo htmlspecialchars($entry['date']); ?></td>
                                    <td><?php echo htmlspecialchars($entry['project']); ?></td>
                                    <td><?php echo htmlspecialchars($entry['hours']); ?></td>
                                    <td><?php echo htmlspecialchars($entry['description']); ?></td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>

using UnityEngine;
using UnityEngine.UI;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq; // Für JObject
using System.Collections.Generic;
using System.Text;
using System.Net.Sockets;
using System.IO; // Für Path und File
using System.Linq; // Für Last()

public class FeedbackManager : MonoBehaviour
{
    public Dropdown exerciseDropdown;
    public Dropdown modelDropdown;
    public Button startButton;
    public TsHumanAnimator tsHumanAnimator;
    public Text serverStatusText; 

    private TcpClient client;
    private NetworkStream stream;
    private bool isSendingData = false;

    private List<Dictionary<string, object>> frameBuffer = new List<Dictionary<string, object>>();
    public int bufferSize = 5; // Frames pro Batch
    public float sendInterval = 0.1f; // Sendehäufigkeit (10 Hz)
    private float timeSinceLastSend = 0f;

    void Start()
    {
        if (exerciseDropdown == null || modelDropdown == null || startButton == null || tsHumanAnimator == null)
        {
            Debug.LogError("Nicht alle UI-Elemente oder der Animator sind zugewiesen!");
            return;
        }

        PopulateExerciseDropdown();
        PopulateModelDropdown();

        ConnectToServer();
        startButton.onClick.AddListener(StartFeedback);
    }

    void Update()
    {
        if (isSendingData)
        {
            timeSinceLastSend += Time.deltaTime;
            if (timeSinceLastSend >= sendInterval)
            {
                SendSuitData();
                timeSinceLastSend = 0f;
            }
        }
    }

    async void ConnectToServer()
    {
        try
        {
            client = new TcpClient();
            await client.ConnectAsync("127.0.0.1", 6667);
            stream = client.GetStream();
            Debug.Log("Verbunden mit dem Python-Server.");
            UpdateServerStatus("Verbunden mit dem Server.", true);
        }
        catch (SocketException e)
        {
            UpdateServerStatus($"Fehler beim Verbinden: {e.Message}", false);
            Debug.LogError($"Fehler beim Verbinden mit dem Server: {e.Message}");
        }
    }

    public void StartFeedback()
    {
        if (tsHumanAnimator == null)
        {
            Debug.LogError("TsHumanAnimator ist nicht zugewiesen!");
            return;
        }

        isSendingData = true;
        Debug.Log("Feedback gestartet.");
    }

    void SendSuitData()
    {
        Debug.Log("test");
        var data = new Dictionary<string, object>
        {
            { "exerciseType", exerciseDropdown.options[exerciseDropdown.value].text },
            { "model", modelDropdown.options[modelDropdown.value].text },
            { "replayPosition", GetReplayPositionData() },
            { "replayRotation", GetReplayRotationData() }
        };

        frameBuffer.Add(data);

        if (frameBuffer.Count >= bufferSize)
        {
            try
            {
                string jsonData = JsonConvert.SerializeObject(frameBuffer, Formatting.Indented);
                byte[] dataBytes = Encoding.UTF8.GetBytes(jsonData + "\nEND_OF_JSON\n");
                stream.Write(dataBytes, 0, dataBytes.Length);
                stream.Flush();
                frameBuffer.Clear();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Fehler beim Senden der Daten: {e.Message}");
            }
        }
    }

    void PopulateExerciseDropdown()
    {
        // Dynamisch den Pfad zur JSON-Datei bestimmen
        string path = Path.Combine(Application.dataPath, "../../PythonFiles__MovementAssessmentWithTeslasuit/model/model_accuracies.json");
        path = Path.GetFullPath(path); // Konvertiere den Pfad zu einem absoluten Pfad

        if (!File.Exists(path))
        {
            Debug.LogError($"Die Datei model_accuracies.json wurde nicht gefunden unter: {path}");
            return;
        }

        // JSON-Datei einlesen
        string jsonContent = File.ReadAllText(path);
        JObject metrics = JObject.Parse(jsonContent);

        exerciseDropdown.ClearOptions();
        foreach (var exercise in metrics)
        {
            exerciseDropdown.options.Add(new Dropdown.OptionData(exercise.Key)); // Füge den Übungstyp hinzu
        }
        exerciseDropdown.RefreshShownValue();
    }

    void PopulateModelDropdown()
    {
        // Dynamisch den Pfad zur JSON-Datei bestimmen
        string path = Path.Combine(Application.dataPath, "../../PythonFiles__MovementAssessmentWithTeslasuit/model/model_accuracies.json");
        path = Path.GetFullPath(path); // Konvertiere den Pfad zu einem absoluten Pfad

        if (!File.Exists(path))
        {
            Debug.LogError($"Die Datei model_accuracies.json wurde nicht gefunden unter: {path}");
            return;
        }

        // JSON-Datei einlesen
        string jsonContent = File.ReadAllText(path);
        JObject metrics = JObject.Parse(jsonContent);

        modelDropdown.ClearOptions();
        foreach (var exercise in metrics)
        {
            foreach (var model in exercise.Value)
            {
                string modelName = $"{exercise.Key}_{model.Path.Split('.').Last()}";
                string accuracy = model.First["accuracy"].ToString(); // Genauigkeit
                modelDropdown.options.Add(new Dropdown.OptionData($"{modelName} - Genauigkeit: {accuracy}"));
            }
        }
        modelDropdown.RefreshShownValue();
    }

    Dictionary<string, Dictionary<string, float>> GetReplayPositionData()
    {
        var replayPosition = new Dictionary<string, Dictionary<string, float>>();
        foreach (var kvp in tsHumanAnimator.BoneTransforms)
        {
            replayPosition[kvp.Key.ToString()] = new Dictionary<string, float>
            {
                { "x", Mathf.Round(kvp.Value.position.x * 100f) / 100f },
                { "y", Mathf.Round(kvp.Value.position.y * 100f) / 100f },
                { "z", Mathf.Round(kvp.Value.position.z * 100f) / 100f }
            };
        }
        return replayPosition;
    }

    Dictionary<string, Dictionary<string, float>> GetReplayRotationData()
    {
        var replayRotation = new Dictionary<string, Dictionary<string, float>>();
        foreach (var kvp in tsHumanAnimator.BoneTransforms)
        {
            replayRotation[kvp.Key.ToString()] = new Dictionary<string, float>
            {
                { "x", Mathf.Round(kvp.Value.rotation.eulerAngles.x * 100f) / 100f },
                { "y", Mathf.Round(kvp.Value.rotation.eulerAngles.y * 100f) / 100f },
                { "z", Mathf.Round(kvp.Value.rotation.eulerAngles.z * 100f) / 100f }
            };
        }
        return replayRotation;
    }

    void UpdateServerStatus(string message, bool isConnected = false)
    {
        serverStatusText.text = message;
        serverStatusText.color = isConnected ? Color.green : Color.red;
    }

    void OnDestroy()
    {
        if (stream != null) stream.Close();
        if (client != null) client.Close();
    }
}

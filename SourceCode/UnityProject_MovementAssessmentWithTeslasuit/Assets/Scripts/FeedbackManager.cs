using UnityEngine;
using UnityEngine.UI;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq; // Für JObject
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Net.Sockets;
using System.IO; // Für Path und File
using System.Linq;
using TsSDK; // Falls TsHumanBoneIndex hier definiert ist
using TsAPI.Types; // Falls der Typ hier definiert ist

public class FeedbackManager : MonoBehaviour
{
    public Dropdown exerciseDropdown;
    public Dropdown modelDropdown;
    public Button startButton;
    public TsHumanAnimator tsHumanAnimator;
    public Text serverStatusText;
    public GameObject feedbackPanel;
    public Text feedbackText;
    public GameObject feedbackUI;
    [SerializeField]
    private TsHapticPlayer hapticPlayer;

    [Range(1, 150)]
    public int frequency;

    [Range(1, 100)]
    public int amplitude;

    [Range(1, 320)]
    public int pulseWidth;

    [Range(10, 10000)]
    public int durationMs;

    private TcpClient client;
    private NetworkStream stream;
    private bool isSendingData = false;

    private List<Dictionary<string, object>> frameBuffer = new List<Dictionary<string, object>>();
    public int bufferSize = 5; // Frames pro Batch
    public float sendInterval = 0.1f; // Sendehäufigkeit (10 Hz)
    private float timeSinceLastSend = 0f;
    private Dictionary<string, List<KeyValuePair<string, float>>> exerciseToModels;
    private Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>> hapticChannels = new Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>>();
    private Dictionary<string, TsHumanBoneIndex> jointNameToBoneIndex = new Dictionary<string, TsHumanBoneIndex>
    {
        { "Hips", TsHumanBoneIndex.Hips },
        { "LeftUpperLeg", TsHumanBoneIndex.LeftUpperLeg },
        { "RightUpperLeg", TsHumanBoneIndex.RightUpperLeg },
        { "LeftLowerLeg", TsHumanBoneIndex.LeftLowerLeg },
        { "RightLowerLeg", TsHumanBoneIndex.RightLowerLeg },
        { "LeftFoot", TsHumanBoneIndex.LeftFoot },
        { "RightFoot", TsHumanBoneIndex.RightFoot },
        { "Spine", TsHumanBoneIndex.Spine },
        { "Chest", TsHumanBoneIndex.Chest },
        { "UpperSpine", TsHumanBoneIndex.UpperSpine },
        { "Neck", TsHumanBoneIndex.Neck },
        { "Head", TsHumanBoneIndex.Head },
        { "LeftShoulder", TsHumanBoneIndex.LeftShoulder },
        { "RightShoulder", TsHumanBoneIndex.RightShoulder },
        { "LeftUpperArm", TsHumanBoneIndex.LeftUpperArm },
        { "RightUpperArm", TsHumanBoneIndex.RightUpperArm },
        { "LeftLowerArm", TsHumanBoneIndex.LeftLowerArm },
        { "RightLowerArm", TsHumanBoneIndex.RightLowerArm },
        { "LeftHand", TsHumanBoneIndex.LeftHand },
        { "RightHand", TsHumanBoneIndex.RightHand },
        { "LeftThumbProximal", TsHumanBoneIndex.LeftThumbProximal },
        { "LeftThumbIntermediate", TsHumanBoneIndex.LeftThumbIntermediate },
        { "LeftThumbDistal", TsHumanBoneIndex.LeftThumbDistal },
        { "LeftIndexProximal", TsHumanBoneIndex.LeftIndexProximal },
        { "LeftIndexIntermediate", TsHumanBoneIndex.LeftIndexIntermediate },
        { "LeftIndexDistal", TsHumanBoneIndex.LeftIndexDistal },
        { "LeftMiddleProximal", TsHumanBoneIndex.LeftMiddleProximal },
        { "LeftMiddleIntermediate", TsHumanBoneIndex.LeftMiddleIntermediate },
        { "LeftMiddleDistal", TsHumanBoneIndex.LeftMiddleDistal },
        { "LeftRingProximal", TsHumanBoneIndex.LeftRingProximal },
        { "LeftRingIntermediate", TsHumanBoneIndex.LeftRingIntermediate },
        { "LeftRingDistal", TsHumanBoneIndex.LeftRingDistal },
        { "LeftLittleProximal", TsHumanBoneIndex.LeftLittleProximal },
        { "LeftLittleIntermediate", TsHumanBoneIndex.LeftLittleIntermediate },
        { "LeftLittleDistal", TsHumanBoneIndex.LeftLittleDistal },
        { "RightThumbProximal", TsHumanBoneIndex.RightThumbProximal },
        { "RightThumbIntermediate", TsHumanBoneIndex.RightThumbIntermediate },
        { "RightThumbDistal", TsHumanBoneIndex.RightThumbDistal },
        { "RightIndexProximal", TsHumanBoneIndex.RightIndexProximal },
        { "RightIndexIntermediate", TsHumanBoneIndex.RightIndexIntermediate },
        { "RightIndexDistal", TsHumanBoneIndex.RightIndexDistal },
        { "RightMiddleProximal", TsHumanBoneIndex.RightMiddleProximal },
        { "RightMiddleIntermediate", TsHumanBoneIndex.RightMiddleIntermediate },
        { "RightMiddleDistal", TsHumanBoneIndex.RightMiddleDistal },
        { "RightRingProximal", TsHumanBoneIndex.RightRingProximal },
        { "RightRingIntermediate", TsHumanBoneIndex.RightRingIntermediate },
        { "RightRingDistal", TsHumanBoneIndex.RightRingDistal },
        { "RightLittleProximal", TsHumanBoneIndex.RightLittleProximal },
        { "RightLittleIntermediate", TsHumanBoneIndex.RightLittleIntermediate },
        { "RightLittleDistal", TsHumanBoneIndex.RightLittleDistal }
    };

    void Start()
    {
        if (exerciseDropdown == null || modelDropdown == null || startButton == null || tsHumanAnimator == null || feedbackPanel == null || feedbackText == null || feedbackUI == null || hapticPlayer == null)
        {
            UnityEngine.Debug.LogError("Nicht alle UI-Elemente oder der HapticPlayer sind zugewiesen!");
            return;
        }

        StartCoroutine(InitializeFeedbackManager());
        PopulateExerciseDropdown();
        ConnectToServer();
        startButton.onClick.AddListener(StartFeedback);
        exerciseDropdown.onValueChanged.AddListener(UpdateModelDropdown);
    }

    private System.Collections.IEnumerator InitializeFeedbackManager()
    {
        // Warte auf die Initialisierung des HapticPlayers
        yield return StartCoroutine(WaitForHapticPlayerInitialization());

        // Initialisiere Haptic-Kanäle
        InitializeHapticChannels();
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
            UpdateServerStatus("Connected", true);
            ListenForServerMessages();
        }
        catch (SocketException e)
        {
            UpdateServerStatus("Not Connected", false);
            UnityEngine.Debug.Log($"Error while Connecting: {e.Message}");
        }
    }

    public void StartFeedback()
    {
        isSendingData = true;
        feedbackUI.SetActive(false);
        feedbackPanel.SetActive(true);
        feedbackText.text = "";
    }

    void SendSuitData()
    {
        string selectedExercise = exerciseDropdown.options[exerciseDropdown.value].text;
        string selectedModel = modelDropdown.options[modelDropdown.value].text.Split('-')[0].Trim();

        // Modellnamen für den Pfad und die Servernachricht anpassen
        string modelFileName = selectedModel == "k" ? "k-NN" : selectedModel; // "k" wird zu "k-NN"

        // Originaldaten senden
        var data = new Dictionary<string, object>
        {
            { "exerciseType", selectedExercise },
            { "model", modelFileName }, // Angepasster Modellname für den Server
            { "replayPosition", GetReplayPositionData() },
            { "replayRotation", GetReplayRotationData() }
        };

        frameBuffer.Add(data);

        if (frameBuffer.Count >= bufferSize)
        {
            try
            {
                string jsonData = JsonConvert.SerializeObject(frameBuffer);
                byte[] dataBytes = Encoding.UTF8.GetBytes(jsonData + "\nEND_OF_JSON\n");
                stream.Write(dataBytes, 0, dataBytes.Length);
                frameBuffer.Clear();
            }
            catch (System.Exception e)
            {
                UnityEngine.Debug.LogError($"Fehler beim Senden der Daten: {e.Message}");
            }
        }
    }

    private void InitializeHapticChannels()
    {
        UnityEngine.Debug.Log("Starte die Validierung der Haptic-Kanäle...");
        ValidateChannels();

        if (hapticChannels.Count == 0)
        {
            UnityEngine.Debug.LogError("Keine Haptic-Kanäle gefunden. Überprüfe die Verbindung zum Teslasuit.");
        }
        else
        {
            UnityEngine.Debug.Log("Haptic-Kanäle erfolgreich geladen und validiert.");
        }
    }

    private System.Collections.IEnumerator WaitForHapticPlayerInitialization()
    {
        while (hapticPlayer == null)
        {
            UnityEngine.Debug.LogWarning("HapticPlayer ist null. Warte auf Initialisierung...");
            yield return null;
        }

        while (hapticPlayer.Device == null)
        {
            UnityEngine.Debug.LogWarning("Warte auf Initialisierung des HapticPlayer.Device...");
            yield return null;
        }

        while (hapticPlayer.Device.Mapping2d == null)
        {
            UnityEngine.Debug.LogWarning("Warte auf Initialisierung des Mapping2d...");
            yield return null;
        }

        UnityEngine.Debug.Log("HapticPlayer ist vollständig initialisiert. Lade Kanäle...");
        InitializeHapticChannels();
    }

    private void ValidateChannels()
    {
        // Prüfen, ob der HapticPlayer und das Device initialisiert sind
        if (hapticPlayer == null)
        {
            UnityEngine.Debug.LogError("HapticPlayer ist null. Stelle sicher, dass er korrekt zugewiesen ist.");
            return;
        }

        if (hapticPlayer.Device == null)
        {
            UnityEngine.Debug.LogError("HapticPlayer.Device ist null. Teslasuit scheint nicht verbunden zu sein.");
            return;
        }

        if (hapticPlayer.Device.Mapping2d == null)
        {
            UnityEngine.Debug.LogError("HapticPlayer.Device.Mapping2d ist null. Mapping-Daten sind nicht verfügbar.");
            return;
        }

        // Kanäle laden
        hapticChannels.Clear();
        var channels = hapticPlayer.Device.Mapping2d.ElectricChannels;
        foreach (var channel in channels)
        {
            if (!hapticChannels.ContainsKey(channel.BoneIndex))
            {
                hapticChannels[channel.BoneIndex] = new List<IMapping2dElectricChannel>();
            }
            hapticChannels[channel.BoneIndex].Add(channel);
        }

        UnityEngine.Debug.Log($"Haptic-Kanäle erfolgreich validiert. {hapticChannels.Count} Körperteile gefunden.");
    }

    async void ListenForServerMessages()
    {
        byte[] buffer = new byte[1024];
        StringBuilder messageBuilder = new StringBuilder();

        while (client != null && client.Connected)
        {
            try
            {
                int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                if (bytesRead > 0)
                {
                    string received = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    messageBuilder.Append(received);

                    // Process complete messages
                    if (messageBuilder.ToString().Contains("\nEND_OF_JSON\n"))
                    {
                        string[] messages = messageBuilder.ToString().Split(new[] { "\nEND_OF_JSON\n" }, StringSplitOptions.RemoveEmptyEntries);

                        foreach (string msg in messages)
                        {
                            try
                            {
                                HandleServerMessage(msg.Trim());
                            }
                            catch (JsonReaderException ex)
                            {
                                UnityEngine.Debug.LogError($"JSON Parsing Error: {ex.Message}. Raw message: {msg}");
                            }
                        }

                        // Clear processed messages
                        messageBuilder.Clear();
                    }
                }
            }
            catch (IOException e)
            {
                UnityEngine.Debug.LogError($"Connection error: {e.Message}");
                UpdateServerStatus("Connection lost.", false);
                break;
            }
        }
    }

    void HandleServerMessage(string message)
    {
        try
        {
            UnityEngine.Debug.Log($"Received message: {message}");
            var response = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);

            // Verarbeite den Status der Fehlstellung
            if (response.ContainsKey("misalignmentStatus"))
            {
                string misalignmentStatus = response["misalignmentStatus"].ToString();
                feedbackText.text = misalignmentStatus;

                // Setze die Farbe basierend auf dem Status
                if (misalignmentStatus == "Fehlhaltung erkannt")
                {
                    feedbackText.color = Color.red; // Rot für Fehlstellung
                }
                else if (misalignmentStatus == "Keine Fehlhaltung")
                {
                    feedbackText.color = Color.green; // Grün für keine Fehlstellung
                }
                else
                {
                    feedbackText.color = Color.black; // Standardfarbe für unbekannte Fälle
                }
            }

            // Verarbeite die Abweichungen
            if (response.ContainsKey("deviations"))
            {
                var deviations = JsonConvert.DeserializeObject<List<Dictionary<string, object>>>(response["deviations"].ToString());

                // Haptisches Feedback nur bei Fehlstellung
                if (feedbackText.text == "Fehlhaltung erkannt")
                {
                    foreach (var deviation in deviations)
                    {
                        string joint = deviation["joint"].ToString();
                        var vector = deviation["deviation"] as JArray;

                        // Trigger haptic feedback and highlight deviation
                        HighlightDeviation(joint, new Vector3(
                            float.Parse(vector[0].ToString()),
                            float.Parse(vector[1].ToString()),
                            float.Parse(vector[2].ToString())
                        ));

                        TriggerHapticFeedback(joint, 1); // Feedback nur bei Fehlstellung
                    }
                }
                else
                {
                    UnityEngine.Debug.Log("Keine Fehlhaltung erkannt, kein haptisches Feedback ausgelöst.");
                }
            }
        }
        catch (JsonReaderException ex)
        {
            UnityEngine.Debug.LogError($"JSON Parsing Error: {ex.Message}. Raw message: {message}");
        }
    }

    void HighlightDeviation(string jointName, Vector3 deviation)
    {
        // Map jointName to TsHumanBoneIndex
        if (!jointNameToBoneIndex.TryGetValue(jointName, out TsHumanBoneIndex boneIndex))
        {
            UnityEngine.Debug.LogError($"Ungültiger Gelenkname: {jointName}");
            return;
        }

        // Ensure the BoneTransform exists for the boneIndex
        if (!tsHumanAnimator.BoneTransforms.TryGetValue(boneIndex, out Transform boneTransform))
        {
            UnityEngine.Debug.LogError($"Kein Transform für {boneIndex} gefunden.");
            return;
        }

        // Set the color based on the deviation intensity
        Renderer renderer = boneTransform.GetComponent<Renderer>();
        if (renderer == null)
        {
            UnityEngine.Debug.LogWarning($"Kein Renderer für {jointName} gefunden, kann nicht farblich markiert werden.");
            return;
        }

        // Set color: red for significant deviation, yellow for mild, default is no highlight
        float intensity = deviation.magnitude;
        if (intensity > 0.1f) // Threshold für signifikante Abweichung
        {
            renderer.material.color = intensity > 0.5f ? Color.red : Color.yellow;
        }
        else
        {
            renderer.material.color = Color.white; // Zurücksetzen
        }
    }

    void PopulateExerciseDropdown()
    {
        string path = Path.Combine(Application.dataPath, "../../PythonFiles__MovementAssessmentWithTeslasuit/model/model_accuracies.json");
        path = Path.GetFullPath(path);

        if (!File.Exists(path))
        {
            UnityEngine.Debug.LogError($"Die Datei model_accuracies.json wurde nicht gefunden unter: {path}");
            return;
        }

        string jsonContent = File.ReadAllText(path);
        JObject metrics = JObject.Parse(jsonContent);

        exerciseDropdown.ClearOptions();
        exerciseToModels = new Dictionary<string, List<KeyValuePair<string, float>>>();

        foreach (var exercise in metrics)
        {
            exerciseDropdown.options.Add(new Dropdown.OptionData(exercise.Key));

            var models = new List<KeyValuePair<string, float>>();
            foreach (var model in ((JObject)exercise.Value).Properties())
            {
                string modelName = model.Name;
                float accuracy = model.Value["accuracy"].ToObject<float>();
                models.Add(new KeyValuePair<string, float>(modelName, accuracy));
            }
            exerciseToModels[exercise.Key] = models;
        }

        exerciseDropdown.RefreshShownValue();

        if (exerciseDropdown.options.Count > 0)
        {
            UpdateModelDropdown(0);
        }
    }

    void UpdateModelDropdown(int exerciseIndex)
    {
        if (exerciseIndex < 0 || exerciseIndex >= exerciseDropdown.options.Count)
            return;

        string selectedExercise = exerciseDropdown.options[exerciseIndex].text;

        modelDropdown.ClearOptions();

        if (exerciseToModels.ContainsKey(selectedExercise))
        {
            foreach (var model in exerciseToModels[selectedExercise])
            {
                modelDropdown.options.Add(new Dropdown.OptionData($"{model.Key} - Precision: {model.Value:F3}"));
            }
        }

        modelDropdown.RefreshShownValue();
    }

    public void TriggerHapticFeedback(string jointName, float intensity)
    {
        // Map jointName to TsHumanBoneIndex
        if (!jointNameToBoneIndex.TryGetValue(jointName, out TsHumanBoneIndex boneIndex))
        {
            UnityEngine.Debug.LogError($"Ungültiger Gelenkname: {jointName}");
            return;
        }

        // Prüfen, ob Haptik-Kanäle für das Gelenk vorhanden sind
        if (!hapticChannels.ContainsKey(boneIndex))
        {
            UnityEngine.Debug.LogError($"Keine Haptik-Kanäle für {boneIndex} gefunden.");
            return;
        }

        // Feedback nur für signifikante Intensität abgeben (Threshold)
        if (intensity < 0.2f) // Set threshold for minor deviations
        {
            UnityEngine.Debug.Log($"Abweichung für {jointName} zu gering ({intensity}), kein Feedback nötig.");
            return;
        }

        // Konfiguriere Haptik basierend auf Intensität
        frequency = Mathf.Clamp((int)(50 * intensity), 1, 100); // Weniger aggressive Frequenz
        amplitude = Mathf.Clamp((int)(30 * intensity), 1, 50);  // Reduzierte Amplitude
        pulseWidth = Mathf.Clamp((int)(150 * intensity), 1, 200); // Kürzere Pulse
        durationMs = Mathf.Clamp((int)(300 * intensity), 100, 500); // Kürzere Dauer

        // Feedback erstellen
        var channelGroup = hapticChannels[boneIndex];
        var hapticPlayable = hapticPlayer.CreateTouch(frequency, amplitude, pulseWidth, durationMs);

        if (hapticPlayable != null)
        {
            // Limitiere Feedback auf maximal 2 Kanäle
            int maxChannels = Mathf.Min(channelGroup.Count, 2);
            for (int i = 0; i < maxChannels; i++)
            {
                hapticPlayable.AddChannel(channelGroup[i]);
            }

            hapticPlayable.Play();
            UnityEngine.Debug.Log($"Haptisches Feedback für {jointName} mit Intensität {intensity} ausgelöst.");
        }
        else
        {
            UnityEngine.Debug.LogError($"Fehler beim Erstellen des Haptik-Feedbacks für {jointName}");
        }
    }

    void UpdateServerStatus(string message, bool isConnected = false)
    {
        serverStatusText.text = message;
        serverStatusText.color = isConnected ? Color.green : Color.red;
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

    class DeviationData
    {
        public string joint { get; set; }
        public float[] deviation { get; set; }
        public float intensity { get; set; }

        public Vector3 GetDeviationVector()
        {
            if (deviation != null && deviation.Length == 3)
            {
                return new Vector3(deviation[0], deviation[1], deviation[2]);
            }
            return Vector3.zero; // Default if deviation is invalid
        }
    }
}
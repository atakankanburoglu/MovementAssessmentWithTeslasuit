using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TrainingManager : MonoBehaviour
{
    //Sample Setting Panel
    [SerializeField]
    private Dropdown trainingTypeDropDown;
    [SerializeField]
    private TMP_InputField subjectIDInput;
    [SerializeField]
    private GameObject sampleSettingPanel;

    //Recording Panel
    [SerializeField]
    private GameObject startButton;
    [SerializeField]
    private GameObject pauseButton;
    [SerializeField]
    private GameObject saveButton;
    [SerializeField]
    private GameObject recordingPanel;

    [SerializeField]
    private Dropdown sampleTypeDropDown;

    public TsHumanAnimator tsHumanAnimator;

    private DataGateway dataGateway;

    float timer;
    private bool shouldSave;
    private float timeInterval = 0.5f;


    private ReplayObject infoToJSon;
    string path;

    void Start()
    {
        path = Application.dataPath + "/JsonAttempts/";
        dataGateway = FindObjectOfType<DataGateway>();

        FillTrainingTypeDropDown();
    }

    void Update()
    {
        timer += Time.deltaTime;
        if (shouldSave && timer > timeInterval)
        {
            //Do this for Replay
            ReplayInfo rp = new ReplayInfo();
            foreach (KeyValuePair<TsHumanBoneIndex, Transform> kvp in tsHumanAnimator.BoneTransforms)
            {
                rp.replayPosition.Add(kvp.Key, kvp.Value.position);
                rp.replayRotation.Add(kvp.Key, kvp.Value.rotation.eulerAngles);
                rp.replayRotationQuaternion.Add(kvp.Key, MyQuaternion.ConverToMyQuat(kvp.Value.rotation));
            }

            infoToJSon.replayInfo.Add(rp);

            //Do this for Model Training/Testing
            TrainingType trainingType = (TrainingType)Enum.Parse(typeof(TrainingType), trainingTypeDropDown.options[trainingTypeDropDown.value].text);
            ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, Time.time);
            dataGateway.PythonClient.pushSuitData(imuDataObject);
        }
    }


    void FillTrainingTypeDropDown()
    {
        string[] names = Enum.GetNames(typeof(TrainingType));
        trainingTypeDropDown.ClearOptions();
        trainingTypeDropDown.AddOptions(new List<string>(names));
    }

    public void CreateNewSubject()
    {
        if (subjectIDInput.text == string.Empty)
        {
            Debug.LogError("Please enter a name for this subject");
            return;
        }
        infoToJSon = new ReplayObject() { subjectName = subjectIDInput.text, trainingType = (TrainingType)Enum.Parse(typeof(TrainingType), trainingTypeDropDown.options[trainingTypeDropDown.value].text) };
        recordingPanel.SetActive(true);
        sampleSettingPanel.SetActive(false);


        Debug.Log("object created");
    }
    public void StartRecording()
    {
        if (infoToJSon == null) return;
        shouldSave = true;
    }
    public void StopRecording()
    {
        shouldSave = false;
    }
    public void SaveRecording()
    {
        if (!shouldSave)
        {
            Debug.Log("json");
            string json = JsonConvert.SerializeObject(infoToJSon.replayInfo.ToArray(), Formatting.Indented);

            //write string to file
            System.IO.File.WriteAllText(string.Concat(path, $"{infoToJSon.subjectName}", "_", $"{ infoToJSon.trainingType}", ".json"), json);
            infoToJSon = null;

            SampleType sampleType = (SampleType)Enum.Parse(typeof(SampleType), sampleTypeDropDown.options[sampleTypeDropDown.value].text);
            dataGateway.PythonClient.finishSuitTrainingData(sampleType);
        }
        FillTrainingTypeDropDown();
        subjectIDInput.text = null;
    }

}

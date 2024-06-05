using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class RecordingManager : MonoBehaviour
{
    //Sample Setting Panel
    [SerializeField]
    private Dropdown exerciseTypeDropDownSample;
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

    private bool shouldSave;
    private float timeInterval = 10.0f;


    private ReplayObject infoToJSon;
    string path;

    [SerializeField]
    private Text startCountdown;
    [SerializeField]
    private Text timerCountdown;


    void Start()
    {
        path = Application.dataPath + "/JsonAttempts/";
        dataGateway = FindObjectOfType<DataGateway>();

        FillExerciseTypeDropDownSample();
    }

    void Update()
    {
        if (startCountdown.text == "0")
        {
            timeInterval -= Time.deltaTime;
            if (shouldSave)
            {
                timerCountdown.gameObject.SetActive(true);
                timerCountdown.text = (timeInterval).ToString("0");

                //Do this for Replay
                ReplayInfo rp = new ReplayInfo();
                foreach (KeyValuePair<TsHumanBoneIndex, Transform> kvp in tsHumanAnimator.BoneTransforms)
                {
                    rp.replayPosition.Add(kvp.Key, kvp.Value.position);
                    rp.replayRotation.Add(kvp.Key, kvp.Value.rotation.eulerAngles);
                    rp.replayRotationQuaternion.Add(kvp.Key, MyQuaternion.ConverToMyQuat(kvp.Value.rotation));
                }

                infoToJSon.replayInfo.Add(rp);

                if (tsHumanAnimator.ImuData.Count > 0)
                {
                    ExerciseType exerciseType = (ExerciseType)Enum.Parse(typeof(ExerciseType), exerciseTypeDropDownSample.options[exerciseTypeDropDownSample.value].text);
                    ImuDataObject imuDataObject = new ImuDataObject(exerciseType, tsHumanAnimator.ImuData, timeInterval);
                    dataGateway.PushSuitData(ApplicationMode.Recording, imuDataObject);
                }
            }
        }
        if(timeInterval < 0)
        {
            timeInterval = 10.0f;
        }
    }


    void FillExerciseTypeDropDownSample()
    {
        string[] names = Enum.GetNames(typeof(ExerciseType));
        exerciseTypeDropDownSample.ClearOptions();
        exerciseTypeDropDownSample.AddOptions(new List<string>(names));
    }

    public void CreateNewSubject()
    {
        if (subjectIDInput.text == string.Empty)
        {
            Debug.LogError("Please enter a name for this subject");
            return;
        }
        var exerciseType = (ExerciseType)Enum.Parse(typeof(ExerciseType), exerciseTypeDropDownSample.options[exerciseTypeDropDownSample.value].text);
        infoToJSon = new ReplayObject() { subjectName = subjectIDInput.text, exerciseType = exerciseType};
        recordingPanel.SetActive(true);
        sampleSettingPanel.SetActive(false);

        dataGateway.StartRecording(); 
        Debug.Log("object created");
    }
    public void StartRecording()
    {
        if (infoToJSon == null) return;
        shouldSave = true;
        timeInterval = 10.0f;
    }
    public void StopRecording()
    {
        shouldSave = false;
    }
    public void SaveRecording()
    {
        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;
        if (!shouldSave)
        {
            Debug.Log("json");
            string json = JsonConvert.SerializeObject(infoToJSon.replayInfo.ToArray(), Formatting.Indented);
            SampleType sampleType = (SampleType)Enum.Parse(typeof(SampleType), sampleTypeDropDown.options[sampleTypeDropDown.value].text);

            //write string to file
            System.IO.File.WriteAllText(string.Concat(path, infoToJSon.subjectName, "_", infoToJSon.exerciseType, "_", sampleType, ".json"), json);
            infoToJSon = null;

            ExerciseType exerciseType = (ExerciseType)Enum.Parse(typeof(ExerciseType), exerciseTypeDropDownSample.options[exerciseTypeDropDownSample.value].text);
            SampleDataObject sampleDataObject = new SampleDataObject(subjectIDInput.text, exerciseType, sampleType);
            dataGateway.SaveRecording(sampleDataObject);
        }
        FillExerciseTypeDropDownSample();
        subjectIDInput.text = null; 
    }

    public void Cancel()
    {
        FillExerciseTypeDropDownSample();
        subjectIDInput.text = null;
        recordingPanel.SetActive(false);
        sampleSettingPanel.SetActive(true);
        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;
        shouldSave = false;
    }
}

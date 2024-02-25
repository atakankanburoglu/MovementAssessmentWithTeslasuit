using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TestingManager : MonoBehaviour
{
    //Real Time Testing Setting Panel
    [SerializeField]
    private TMP_InputField subjectIDsInput;
    [SerializeField]
    private Dropdown algorithmDropDown;
    [SerializeField]
    private Toggle newRecognitionModelRealTimeToggle;
    [SerializeField]
    private GameObject realTimeSettingPanel;

    //Recorded Testing Setting Panel
    [SerializeField]
    private Dropdown recordedExercisesDropDown;
    [SerializeField]
    private Toggle newRecognitionModelRecordedToggle;
    [SerializeField]
    private GameObject recordedSettingPanel;

    [SerializeField]
    private TMP_InputField recognizedExerciseOutput;
    [SerializeField]
    private GameObject recognizedExercisePanel;

    //Recording Panel
    [SerializeField]
    private GameObject startButton;
    [SerializeField]
    private GameObject pauseButton;
    [SerializeField]
    private GameObject stopButton;
    [SerializeField]
    private GameObject feedbackPanel;

    public DataGateway dataGateway;

    private Boolean running;

    public TsHumanAnimator tsHumanAnimator;

    private TrainingType trainingType;

    List<string> recordedExercisesList = new List<string>();

    void Start()
    {
        FillAlgorithmDropDownModel();
        GetRecordedExercisesForDropdown();
    }

    void Update()
    {
        if (running)
        {
            ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, Time.time);
            dataGateway.PythonClient.PushSuitData(imuDataObject);
        }
        if (recordedExercisesList.Count != 0)
        {
            FillRecordedExercisesDropDownModel();
        }
    }

    public void FillRecognizedExcerciseOutputInput(TrainingType trainingType)
    {
        this.trainingType = trainingType;
        recognizedExerciseOutput.text = Enum.GetName(typeof(TrainingType), trainingType);
    }


    void FillAlgorithmDropDownModel()
    {
        string[] algorithms = Enum.GetNames(typeof(Algorithm));
        algorithmDropDown.ClearOptions();
        algorithmDropDown.AddOptions(new List<string>(algorithms));
    }

    public void ChooseAlgorithm()
    {
        String algorithm = algorithmDropDown.options[algorithmDropDown.value].text;
        dataGateway.PythonClient.StartTestingMode(algorithm, true);
    }
    void FillRecordedExercisesDropDownModel()
    {
        recordedExercisesDropDown.ClearOptions();
        recordedExercisesDropDown.AddOptions(recordedExercisesList);
    }

    public void GetRecordedExercisesForDropdown()
    {
        dataGateway.PythonClient.GetRecordedExercises();
    }

    public void SetRecordedExercisesForDropdown(string[] recordedExercises)
    {
        this.recordedExercisesList = new List<string>(recordedExercises);
    }

    public void ChooseRecordedExercise()
    {
        String exercise = recordedExercisesDropDown.options[recordedExercisesDropDown.value].text;
        dataGateway.PythonClient.StartTestingMode(exercise, true);
    }

    public void StartFeedback()
    {
        running = true;
    }
    public void PauseFeedback()
    {
        running = false;
    }
    public void StopFeedback()
    {
        dataGateway.PythonClient.StopTestingMode();
        running = false;
    }

    public void Cancel()
    {
        FillAlgorithmDropDownModel();
        feedbackPanel.SetActive(false);
        realTimeSettingPanel.SetActive(true);
        recordedSettingPanel.SetActive(true);
        recognizedExercisePanel.SetActive(false);
    }
}

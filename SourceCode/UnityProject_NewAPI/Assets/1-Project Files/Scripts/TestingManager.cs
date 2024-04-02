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
    private TMP_InputField subjectIDsRecordedInput;
    [SerializeField]
    private Dropdown algorithmRecordedDropDown;
    [SerializeField]
    private TMP_Dropdown recordedExercisesDropDown;
    private int recordedExercisesDropDownOption;
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
    private float timeInterval = 10.0f;

    public TsHumanAnimator tsHumanAnimator;

    private TrainingType trainingType;

    List<string> recordedExercisesList = new List<string>();

    [SerializeField]
    private Text startCountdown;
    [SerializeField]
    private Text timerCountdown;

    void Start()
    {
        FillAlgorithmDropDownModel();
        GetRecordedExercisesForDropdown();

    }

    void Update()
    {
        if (startCountdown.text == "0") {
            timeInterval -= Time.deltaTime;
            if (running)
            {
                timerCountdown.gameObject.SetActive(true);
                timerCountdown.text = (timeInterval).ToString("0");

                ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, timeInterval);
                dataGateway.PythonClient.PushSuitData(imuDataObject);
            }
        }
        if (recordedExercisesList.Count != 0)
        {
            FillRecordedExercisesDropDownModel();
        }
        if (timeInterval < 0)
        {
            timeInterval = 10.0f;
        }
        recordedExercisesDropDown.value = recordedExercisesDropDownOption;
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
        algorithmRecordedDropDown.ClearOptions();
        algorithmRecordedDropDown.AddOptions(new List<string>(algorithms));
    }

    public void ChooseAlgorithm()
    {
        String algorithm = algorithmDropDown.options[algorithmDropDown.value].text;
        dataGateway.PythonClient.StartTestingMode(subjectIDsInput.text, algorithm, newRecognitionModelRealTimeToggle.isOn);
    }
    void FillRecordedExercisesDropDownModel()
    {
        recordedExercisesDropDown.ClearOptions();
        List<TMP_Dropdown.OptionData> optionList = new List<TMP_Dropdown.OptionData>();
        foreach (String recordedExercises in recordedExercisesList)
        {
            var newOption = new TMP_Dropdown.OptionData();
            newOption.text = recordedExercises;
            optionList.Add(newOption);
        }
        recordedExercisesDropDown.AddOptions(optionList);
    }

    public void GetRecordedExercisesForDropdown()
    {
        dataGateway.PythonClient.GetRecordedExercises();
    }

    public void SetRecordedExercisesForDropdown(string[] recordedExercises)
    {
        this.recordedExercisesList = new List<string>(recordedExercises);
    }

    public void SaveRecordedExerciseDropdownOption()
    {
        recordedExercisesDropDownOption = recordedExercisesDropDown.value;
    }
    public void ChooseRecordedExercise()
    {
        String algorithm = algorithmDropDown.options[algorithmDropDown.value].text;
        String exercise = recordedExercisesDropDown.options[recordedExercisesDropDown.value].text;
        dataGateway.PythonClient.StartRecordedTestingMode(subjectIDsRecordedInput.text, algorithm, exercise, newRecognitionModelRecordedToggle.isOn);
    }

    public void StartFeedback()
    {
        running = true;
        timeInterval = 10.0f;
    }
    public void PauseFeedback()
    {
        running = false;
    }
    public void StopFeedback()
    {
        dataGateway.PythonClient.StopTestingMode();
        running = false;

        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;
    }

    public void Cancel()
    {
        FillAlgorithmDropDownModel();
        feedbackPanel.SetActive(false);
        realTimeSettingPanel.SetActive(true);
        recordedSettingPanel.SetActive(true);
        recognizedExercisePanel.SetActive(false);
        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;
        running = false;
    }
}

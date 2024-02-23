using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TestingManager : MonoBehaviour
{
    //Model Setting Panel
    [SerializeField]
    private Dropdown algorithmDropDown;
    [SerializeField]
    private Toggle newRecognitionModelToggle;
    [SerializeField]
    private GameObject modelSettingPanel;

    [SerializeField]
    private TMP_InputField recognizedExerciseOutput;

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
    void Start()
    {
        FillAlgorithmDropDownModel();
    }

    void Update()
    {
        if (running)
        {
            ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, Time.time);
            dataGateway.PythonClient.PushSuitData(imuDataObject);
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
        modelSettingPanel.SetActive(true);
        recognizedExerciseOutput.gameObject.SetActive(false);
    }
}

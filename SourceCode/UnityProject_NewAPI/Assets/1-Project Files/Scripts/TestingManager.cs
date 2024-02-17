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
    private Dropdown modelDropDown;
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

    List<string> models = new List<string>();
    void Start()
    {
        
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

    public void GetModelsForDropdown()
    {
        dataGateway.PythonClient.GetModels();
    }

    public void SetModelsForDropdown(List<string> models)
    {
        this.models = models;
        FillModelDropDownModel();
    }

    void FillModelDropDownModel()
    {
        modelDropDown.ClearOptions();
        modelDropDown.AddOptions(models);
    }

    public void ChooseModel()
    {
        String model = modelDropDown.options[modelDropDown.value].text;
        dataGateway.PythonClient.StartTestingMode(model, true);
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
        FillModelDropDownModel();
        feedbackPanel.SetActive(false);
        modelSettingPanel.SetActive(true);
        recognizedExerciseOutput.gameObject.SetActive(false);
    }
}

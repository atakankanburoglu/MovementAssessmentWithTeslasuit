using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;
using TsSDK;

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

    [SerializeField]
    private TsHapticPlayer m_hapticPlayer;

    [Range(1, 150)]
    public int frequency;

    [Range(1, 100)]
    public int amplitude;

    [Range(1, 320)]
    public int pulseWidth;

    [Range(10, 10000)]
    public int durationMs;

    public bool looped = false;

    public int currentChannelIndex = 0;

    public TsHumanBoneIndex TargetBoneIndex = TsHumanBoneIndex.LeftThumbDistal;

    private IHapticDynamicPlayable m_hapticPlayable;

    private Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>> m_channels = new Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>>();


    //Feedback Panel
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

    public void GiveFeedback(Dictionary<TsHumanBoneIndex, int> feedback)
    {
        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            if(feedback.TryGetValue(boneIndex, out int value))
            {
                frequency = 150 * value;
                amplitude = 100 * value;
                pulseWidth = 320 * value;
                TargetBoneIndex = boneIndex;
                //Play(currentChannelIndex);
                //TODO: show feedback through arrow
            }
        }
    }

    private void Validate()
    {
        ValidateChannels();
        if (m_hapticPlayable != null)
        {
            m_hapticPlayable.Stop();
        }

        m_hapticPlayable = m_hapticPlayer.CreateTouch(frequency, amplitude, pulseWidth, durationMs);
        m_hapticPlayable.IsLooped = looped;
    }

    private void ValidateChannels()
    {
        m_channels.Clear();
        var channels = m_hapticPlayer.Device.Mapping2d.ElectricChannels;
        foreach (var channel in channels)
        {
            if (!m_channels.ContainsKey(channel.BoneIndex))
            {
                m_channels.Add(channel.BoneIndex, new List<IMapping2dElectricChannel>());
            }
            m_channels[channel.BoneIndex].Add(channel);
        }
    }

    public void Play(int channelIndex)
    {
        Validate();

        if (!m_channels.TryGetValue(TargetBoneIndex, out var channelsGroup))
        {
            return;
        }

        var index = channelIndex % channelsGroup.Count;
        var channel = channelsGroup[index];
        m_hapticPlayable.Play();
        m_hapticPlayable.AddChannel(channel);
    }


    public void StartFeedback()
    {
        running = true;
        timeInterval = 10.0f;
    }
    public void PauseFeedback()
    {
        running = false;
        m_hapticPlayable.IsPaused = !m_hapticPlayable.IsPaused;
    }
    public void StopFeedback()
    {
        dataGateway.PythonClient.StopTestingMode();
        running = false;

        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;

        m_hapticPlayable.Stop();
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

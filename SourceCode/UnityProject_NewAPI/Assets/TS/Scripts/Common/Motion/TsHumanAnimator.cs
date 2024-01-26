using System;
using System.Collections.Generic;
using TsAPI.Types;
using TsSDK;
using UnityEngine;
//* marked places are where i have added something.

public class TsHumanAnimator : MonoBehaviour
{
    [SerializeField]
    private TsMotionProvider m_motionProvider;

    [SerializeField]
    private TsAvatarSettings m_avatarSettings;

    public bool IPose = true;

    private TsHumanBoneIndex m_rootBone = TsHumanBoneIndex.Hips;
    private Dictionary<TsHumanBoneIndex, Transform> m_bonesTransforms = new Dictionary<TsHumanBoneIndex, Transform>();
    //*
    public Dictionary<TsHumanBoneIndex, Transform> BoneTransforms { get { return m_bonesTransforms; } }
    //*
    private Dictionary<TsHumanBoneIndex, TsImuSensorData> m_imuData = new Dictionary<TsHumanBoneIndex, TsImuSensorData>();
    //*
    public Dictionary<TsHumanBoneIndex, TsImuSensorData> ImuData { get { return m_imuData; } }
    //*
    public bool Replay;
    //*
    float IPoseTimer;

    private void Start()
    {
        if (m_avatarSettings == null)
        {
            Debug.LogError("Missing avatar settings for this character.");
            enabled = false;
            return;
        }

        if(!m_avatarSettings.IsValid)
        {
            Debug.LogError("Invalid avatar settings for this character. Check that all required bones is configured correctly.");
            enabled = false;
            return;
        }

        SetupAvatarBones();
    }

    private void SetupAvatarBones()
    {
        //*
        var imuData = m_motionProvider.GetImuData(Time.time);

        foreach (var reqBoneIndex in TsHumanBones.SuitBones)
        {
            var transformName = m_avatarSettings.GetTransformName(reqBoneIndex);
            var boneTransform = TransformUtils.FindChildRecursive(transform, transformName);
            if (boneTransform != null && !m_bonesTransforms.ContainsKey(reqBoneIndex))
            {
                m_bonesTransforms.Add(reqBoneIndex, boneTransform);
            }
            //*
            if (imuData != null)
            {
                m_imuData.Add(reqBoneIndex, imuData.GetSensorData(reqBoneIndex));
            }
        }
    }

    // Update is called once per frame
    private void Update()
    {
        var skeleton = m_motionProvider.GetSkeleton(Time.time);
        //*
        var imuData = m_motionProvider.GetImuData(Time.time);
        //*
        //if replay is true, character will be replayed by TsReplaySaver script
        if(!Replay) Update(skeleton, imuData);
    }

   
    private void Update(ISkeleton skeleton, IImuData imuData)
    {

        if (skeleton == null)
        {
            return;
        }
        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            var poseRotation = m_avatarSettings.GetIPoseRotation(boneIndex);
            var targetRotation = Conversion.TsRotationToUnityRotation(skeleton.GetBoneTransform(boneIndex).rotation);

            TryDoWithBone(boneIndex, (boneTransform) =>
            {
                boneTransform.rotation = targetRotation * poseRotation;
            });
            //*
            TryDoWithSensorData(boneIndex, (tsImuSensorData) =>
            {
                tsImuSensorData = imuData.GetSensorData(boneIndex);
            });
        }

        TryDoWithBone(m_rootBone, (boneTransform) =>
        {
            var hipsPos = skeleton.GetBoneTransform(TsHumanBoneIndex.Hips).position;
            boneTransform.transform.position = Conversion.TsVector3ToUnityVector3(hipsPos);
        });

        if (IPose)
        {
            m_motionProvider.Calibrate();
            IPose = false;
        }
    }

    public void Calibrate()
    {
        print("Calibrate");
        m_motionProvider?.Calibrate();
    }
    //*
    public void ReplayUpdate(ReplayInfo ri)
    {
        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            MyQuaternion my;
            Quaternion targetRotation;
            if (ri.replayRotationQuaternion.TryGetValue(boneIndex, out my))
            {
                if (boneIndex == TsHumanBoneIndex.Hips)
                {
                    targetRotation = Inverse(MyQuaternion.ConvertToQuat(my),true,true,true);
                }else
                targetRotation = MyQuaternion.ConvertToQuat(my);
            }
            else continue;


            TryDoWithBone(boneIndex, (boneTransform) =>
            {
                boneTransform.rotation = targetRotation;
            });
        }
        TryDoWithBone(m_rootBone, (boneTransform) =>
        {
            boneTransform.transform.position = ri.replayPosition[TsHumanBoneIndex.Hips];
        });

    }

    private void TryDoWithBone(TsHumanBoneIndex boneIndex, Action<Transform> action)
    {
        if (!m_bonesTransforms.TryGetValue(boneIndex, out var boneTransform))
        {
            return;
        }

        action(boneTransform);
    }

    private void TryDoWithSensorData(TsHumanBoneIndex boneIndex, Action<TsImuSensorData> action)
    {
        if (!m_imuData.TryGetValue(boneIndex, out var imuData))
        {
            return;
        }

        action(imuData);
    }

    //*
    private void OnDrawGizmos()
    {
        Color blue = new Color(0, 0, 1, 125);
        Gizmos.color = blue;
        foreach (KeyValuePair<TsHumanBoneIndex, Transform> kvp in m_bonesTransforms)
        {
           // if( kvp.Key == (TsHumanBoneIndex)12 || kvp.Key == (TsHumanBoneIndex)13)
            Gizmos.DrawSphere(kvp.Value.position, 0.05f);
        }
    }
    public static Quaternion HeadingOffset( Quaternion b)
    {
        Quaternion offset = Inverse(b,true,true,true);
        offset.x = 0f;
        offset.z = 0f;

        float mag = offset.w * offset.w + offset.y * offset.y;

        offset.w /= Mathf.Sqrt(mag);
        offset.y /= Mathf.Sqrt(mag);

        return offset;
    }
    private static Quaternion Inverse(Quaternion vector, bool X, bool Y, bool Z)
    {
        vector.x *= X ? -1f : 1f;
        vector.y *= Y ? -1f : 1f;
        vector.z *= Z ? -1f : 1f;
        return vector;
    }
}

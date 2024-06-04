using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using TsAPI.Types;
using TsSDK;
using UnityEditor;
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
    public GameObject ErrorArrow;
    private Dictionary<TsHumanBoneIndex, GameObject> m_errorArrows = new Dictionary<TsHumanBoneIndex, GameObject>();
    private Dictionary<TsHumanBoneIndex, Vector3> m_errorArrowsTransform = new Dictionary<TsHumanBoneIndex, Vector3>();
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
        SetupErrorArrows();
    }

    private void SetupAvatarBones()
    {
        foreach (var reqBoneIndex in TsHumanBones.SuitBones)
        {
            var transformName = m_avatarSettings.GetTransformName(reqBoneIndex);
            var boneTransform = TransformUtils.FindChildRecursive(transform, transformName);
            if (boneTransform != null && !m_bonesTransforms.ContainsKey(reqBoneIndex))
            {
                m_bonesTransforms.Add(reqBoneIndex, boneTransform);
            }
        }
    }

    private void SetupErrorArrows()
    {
        foreach (var reqBoneIndex in TsHumanBones.SuitBones)
        {
            if (!m_errorArrows.ContainsKey(reqBoneIndex))
            {
                m_errorArrows.Add(reqBoneIndex, Instantiate(ErrorArrow));
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
            if (m_imuData.ContainsKey(boneIndex))
            {
                m_imuData[boneIndex] = imuData.GetSensorData(boneIndex);
            }
            else
            {
                m_imuData.Add(boneIndex, imuData.GetSensorData(boneIndex));
            }
            
            if (m_errorArrowsTransform.Count != 0)
            {
                if(boneIndex == TsHumanBoneIndex.Hips && m_errorArrowsTransform.TryGetValue(boneIndex, out var v3)){
                    SetErrorArrow(boneIndex, v3, skeleton.GetBoneTransform(TsHumanBoneIndex.Hips), skeleton.GetBoneTransform(boneIndex));

                }
            }

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

    //*
    public void SetErrorArrow(TsHumanBoneIndex currentBoneIndex, Vector3 v3, TsTransform boneTransformHips, TsTransform boneTransform)
    {
        if (m_errorArrows.TryGetValue(currentBoneIndex, out GameObject errorArrow))
        {
            errorArrow.transform.position = Conversion.TsVector3ToUnityVector3(boneTransform.position);
            Vector3 toLookAtMagn = new Vector3(boneTransform.position.x + (-v3.x), boneTransform.position.y + v3.y, boneTransform.position.z + (-v3.z));
            errorArrow.transform.LookAt(toLookAtMagn);
            errorArrow.transform.rotation = Quaternion.FromToRotation(Conversion.TsVector3ToUnityVector3(boneTransform.position), toLookAtMagn);
            errorArrow.SetActive(true);
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


    //*
    public void ShowErrors(String errors)
    {
        List<TsHumanBoneIndex> errorIndexes = new List<TsHumanBoneIndex>();
        string pattern = @"{[^()]*}|[^()]+";
        MatchCollection matches = Regex.Matches(errors, pattern);
        foreach (Match m in matches)
        {
            String[] entry = m.Value.Split(',');
            if (entry.Length == 5)
            {
                TsHumanBoneIndex currentBoneIndex = (TsHumanBoneIndex)Enum.Parse(typeof(TsHumanBoneIndex), entry[0]);
                float.TryParse(entry[1], System.Globalization.NumberStyles.Number, null, out float value1);
                float.TryParse(entry[2], System.Globalization.NumberStyles.Number, null, out float value2);
                float.TryParse(entry[3], System.Globalization.NumberStyles.Number, null, out float value3);
                //float.TryParse(entry[4], System.Globalization.NumberStyles.Number, null, out float angle);
                Vector3 direction = new Vector3(value1, value2, value3);
                if (m_errorArrowsTransform.ContainsKey(currentBoneIndex))
                {
                    m_errorArrowsTransform[currentBoneIndex] = direction;
                }
                else
                {
                    m_errorArrowsTransform.Add(currentBoneIndex, direction);
                }
                errorIndexes.Add(currentBoneIndex);
            }
        }

        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            if (!errorIndexes.Contains(boneIndex))
            {
                if (m_errorArrows.TryGetValue(boneIndex, out GameObject errorArrow))
                {
                    errorArrow.SetActive(false);
                }
            }
        }
    }


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

import numpy as np
from collections import Counter
from sklearn.utils import resample


def print_class_distribution(labels, dataset_name="Dataset"):
    """
    打印数据集中各个类别的样本数量
    
    Args:
        labels: 标签数组
        dataset_name: 数据集名称
    """
    class_counts = Counter(labels)
    total_samples = len(labels)
    
    print(f"\n{'='*60}")
    print(f"Class distribution in {dataset_name}:")
    print(f"{'='*60}")
    print(f"{'Class':<15} {'Count':<15} {'Percentage':<15}")
    print(f"{'-'*60}")
    
    for class_label in sorted(class_counts.keys()):
        count = class_counts[class_label]
        percentage = (count / total_samples) * 100
        print(f"{str(class_label):<15} {count:<15} {percentage:.2f}%")
    
    print(f"{'-'*60}")
    print(f"{'Total':<15} {total_samples:<15} {'100.00%':<15}")
    print(f"{'='*60}\n")
    
    return class_counts


def upsample_data(data_x, data_y, strategy='balanced', random_state=42):
    """
    对少数类别的样本进行上采样，尽可能保证类别平衡
    
    Args:
        data_x: 特征数据 (numpy array)
        data_y: 标签数据 (numpy array)
        strategy: 上采样策略
            - 'balanced': 将所有类别上采样到最多类别的数量
            - 'median': 将所有类别上采样到中位数类别的数量
            - 'mean': 将所有类别上采样到平均数量
        random_state: 随机种子
    
    Returns:
        upsampled_data_x: 上采样后的特征数据
        upsampled_data_y: 上采样后的标签数据
    """
    # 统计类别分布
    class_counts = Counter(data_y)
    print_class_distribution(data_y, "Original Training Set")
    
    # 确定目标样本数量
    if strategy == 'balanced':
        target_count = max(class_counts.values())
    elif strategy == 'median':
        target_count = int(np.median(list(class_counts.values())))
    elif strategy == 'mean':
        target_count = int(np.mean(list(class_counts.values())))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    print(f"Upsampling strategy: {strategy}")
    print(f"Target samples per class: {target_count}")
    
    # 对每个类别进行上采样
    upsampled_data_x_list = []
    upsampled_data_y_list = []
    
    for class_label in sorted(class_counts.keys()):
        # 获取该类别的所有样本索引
        class_indices = np.where(data_y == class_label)[0]
        class_data_x = data_x[class_indices]
        class_data_y = data_y[class_indices]
        
        current_count = len(class_indices)
        
        if current_count < target_count:
            # 需要上采样
            n_samples_to_generate = target_count - current_count
            
            # 使用有放回抽样进行上采样
            np.random.seed(random_state)
            indices_to_duplicate = np.random.choice(
                current_count, 
                size=n_samples_to_generate, 
                replace=True
            )
            
            # 添加原始样本
            upsampled_data_x_list.append(class_data_x)
            upsampled_data_y_list.append(class_data_y)
            
            # 添加上采样的样本
            upsampled_data_x_list.append(class_data_x[indices_to_duplicate])
            upsampled_data_y_list.append(class_data_y[indices_to_duplicate])
            
            print(f"Class {class_label}: {current_count} -> {target_count} samples (upsampled {n_samples_to_generate} samples)")
        else:
            # 不需要上采样，直接添加
            upsampled_data_x_list.append(class_data_x)
            upsampled_data_y_list.append(class_data_y)
            print(f"Class {class_label}: {current_count} samples (no upsampling needed)")
    
    # 合并所有类别的数据
    upsampled_data_x = np.concatenate(upsampled_data_x_list, axis=0)
    upsampled_data_y = np.concatenate(upsampled_data_y_list, axis=0)
    
    # 打乱数据
    np.random.seed(random_state)
    shuffle_indices = np.random.permutation(len(upsampled_data_y))
    upsampled_data_x = upsampled_data_x[shuffle_indices]
    upsampled_data_y = upsampled_data_y[shuffle_indices]
    
    # 打印上采样后的类别分布
    print_class_distribution(upsampled_data_y, "Upsampled Training Set")
    
    return upsampled_data_x, upsampled_data_y

